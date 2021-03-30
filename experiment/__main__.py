#!/usr/bin/env python

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
