#!/usr/bin/env python
#
# Copyright (c) 2020-2021 Hopenly srl.
#
# This file is part of Ilyde.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import logging
import os
from multiprocessing import Process
import click
import config
from job import Watcher
from agent import websock

import utils

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)


@click.command()
@click.option('-k', '--kind', required=True, type=click.Choice(['WORKSPACE', 'RUN', 'EXPERIMENT'],
                                                               case_sensitive=False))
@click.option('-c', '--command', required=True, type=str)
@click.option('--project-id', required=True, type=str)
@click.option('--project-revision-id', required=True, type=str)
@click.option('--user-id', required=True, type=str)
@click.option('--dataset', multiple=True, type=(str, str, bool))
def main(kind, command, project_id, project_revision_id, user_id, dataset):
    logger = logging.getLogger(__name__)
    # copy project files
    if not os.listdir(config.ILYDE_WORKING_DIR):
        utils.copy_project(project_id, project_revision_id)

    # s3fs credentials
    credentials_file = utils.create_s3fs_credentials()
    # mounting datasets
    bucket_mappings = {}
    for dataset_id, dataset_version, mount_output in dataset:
        bucket, dataset_name = utils.mount_dataset(dataset_id, dataset_version, credentials_file, mount_output)
        if all([bucket, dataset_name]):
            bucket_mappings[dataset_id] = {"bucket": bucket, "name": dataset_name}

    # install other pip dependencies
    if os.path.exists(os.path.join(config.ILYDE_WORKING_DIR, 'requirements.txt')):
        utils.run_command("pip --quiet install -r {}".format(os.path.join(config.ILYDE_WORKING_DIR, 'requirements.txt')))

    # watch working dir for changes
    w = Watcher(config.ILYDE_WORKING_DIR, config.ILYDE_WORKING_DIR_CHANGELOG)
    w.run()

    if kind in ['WORKSPACE']:
        # run start agent
        author = user_id
        p = Process(target=websock.serve, args=(project_id, project_revision_id, author, dataset, bucket_mappings, w))
        p.start()
        # server.serve(project_id, author, watcher=w)

    # finally, start job to run
    logger.info(command)
    utils.run_command(command)

    # sleep 30s
    utils.run_command("sleep 30")
    # stop watching working dir for changes
    w.stop()

    # post job: verify and commit changes
    if kind in ['RUN']:
        author = user_id
        changes = w.get_state()
        if changes is not None:
            message = "From RUN@{}".format(config.ILYDE_JOB_ID)
            utils.commit_project(project_id, message, author, changes)

        for dataset_id, dataset_version, mount_output in dataset:
            if mount_output:
                dataset_path = os.path.join(config.ILYDE_WORKING_DIR, "datasets", "output",
                                            bucket_mappings[dataset_id]["name"])
                if os.listdir(dataset_path):
                    utils.create_dataset_version(dataset_id, bucket_mappings[dataset_id]["bucket"], author)


if __name__ == '__main__':
    main()
