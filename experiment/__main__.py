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
import click
import config
import mlflow
from mlflow.tracking import MlflowClient


log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)


@click.command()
@click.option('--entrypoint', required=True, type=str)
@click.option('--params', multiple=True, type=(str, str))
def main(entrypoint, params):

    parameters = {}
    for name, value in params:
        parameters[name] = value

    active_run = mlflow.projects.run(
        uri="/ilyde",
        entry_point=entrypoint,
        parameters=parameters,
        use_conda=False
    )

    client = MlflowClient()
    # Set a tag and fetch updated run info
    client.set_tag(active_run.run_id, "ilyde.job", config.ILYDE_JOB_ID)


if __name__ == '__main__':

    main()
