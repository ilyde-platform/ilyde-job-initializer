#!/usr/bin/env python

import json
import logging
import os
import click
import config
from job import Watcher
from agent import server

import utils

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)


@click.command()
@click.option('-k', '--kind', required=True, type=click.Choice(['WORKSPACE', 'REGULAR', 'CRON', 'EXPERIMENT',
                                                                'DEPLOYMENT'], case_sensitive=False))
@click.option('-c', '--command', required=True, type=str)
@click.option('--project-id', required=True, type=str)
@click.option('--project-revision-id', required=True, type=str)
@click.option('--user-id', required=True, type=str)
@click.option('--user-username', required=True, type=str)
@click.option('--user-name', required=True, type=str)
@click.option('--dataset', multiple=True, type=(str, str, str, bool))
def main(kind, command, project_id, project_revision_id, user_id, user_username, user_name, dataset):
    logger = logging.getLogger(__name__)

    if kind not in ['DEPLOYMENT']:
        # initialize environment
        # copy project
        utils.copy_project(project_id, project_revision_id)
        # s3fs credentials
        credentials_file = utils.create_s3fs_credentials()
        # mounting datasets
        for dataset_id, dataset_name, related_bucket, writeable in dataset:
            utils.mount_dataset(dataset_name, related_bucket, credentials_file, writeable)
        # install other pip dependencies
        if os.path.exists(os.path.join(config.ILYDE_WORKING_DIR, 'requirements.txt')):
            utils.run_command("pip install -r {}".format(os.path.join(config.ILYDE_WORKING_DIR, 'requirements.txt')))

    # watch working dir for changes
    w = Watcher(config.ILYDE_WORKING_DIR, config.ILYDE_WORKING_DIR_CHANGELOG)
    w.run()

    if kind in ['WORKSPACE']:
        # run start agent
        author = {
            'id': user_id,
            'name': user_name,
            'username': user_username
        }
        server.serve(project_id, author)

    # finally, start job to run
    logger.info('----------Starting Ilyde JOB-------------')
    logger.info(command)
    utils.run_command(command)
    logger.info('----------Job Successfully Executed------------')

    # sleep 30s
    utils.run_command("sleep 30")

    # stop watching working dir for changes
    w.stop()

    # post job: verify and commit changes
    if kind in ['REGULAR', 'CRON']:
        changes = w.get_state()
        if changes is not None:
            message = "From JOB@{}".format(config.ILYDE_JOB_ID)
            author = {
                'id': user_id,
                'name': user_name,
                'username': user_username
            }
            utils.commit_project(project_id, message, author, changes)


if __name__ == '__main__':

    main()
