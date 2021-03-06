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
import asyncio
import errno
import json
import logging
import os
from typing import List

import websockets
from google.protobuf import json_format

import config
from job import Watcher
import utils

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


def diff_revisions(rev1: dict, rev2: dict) -> List[dict]:
    return [f for f in rev1.get("file_tree") if f not in rev2.get("file_tree")]


class JobAgentSocket(object):

    def __init__(self, project_id, project_revision_id, author,
                 datasets, bucket_mappings, watcher: Watcher):
        self.project_id = project_id
        self.author = author
        self.watcher = watcher
        self.datasets = datasets
        self.bucket_mappings = bucket_mappings

        if os.path.exists(config.ILYDE_WORKING_DIR_CONFIG):
            with open(config.ILYDE_WORKING_DIR_CONFIG, ) as f:
                data = json.load(f)
                self.current_project_revision_id = data["revision"]
        else:
            self.current_project_revision_id = project_revision_id
            data = {"revision": project_revision_id}
            # save revision in config
            self.save_config(data)

    @staticmethod
    def save_config(data):
        if not os.path.exists(os.path.dirname(config.ILYDE_WORKING_DIR_CONFIG)):
            try:
                os.makedirs(os.path.dirname(config.ILYDE_WORKING_DIR_CONFIG), exist_ok=True)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(config.ILYDE_WORKING_DIR_CONFIG, "w") as f:
            json.dump(data, f)

    def diff(self):
        revision = utils.last_project_revision(self.project_id)
        diffs = []
        if self.current_project_revision_id != revision.id:
            diffs = diff_revisions(
                json_format.MessageToDict(revision, preserving_proto_field_name=True,
                                          including_default_value_fields=True),
                json_format.MessageToDict(utils.retrieve_project_revision(self.current_project_revision_id),
                                          preserving_proto_field_name=True,
                                          including_default_value_fields=True),
            )

        res = {
            "action": "diff",
            "type": "file_tree",
            "message": diffs
        }

        return json.dumps(res)

    def sync(self):
        revision = utils.last_project_revision(self.project_id)
        if self.current_project_revision_id != revision.id:
            diffs = diff_revisions(
                json_format.MessageToDict(revision, preserving_proto_field_name=True,
                                          including_default_value_fields=True),
                json_format.MessageToDict(utils.retrieve_project_revision(self.current_project_revision_id),
                                          preserving_proto_field_name=True,
                                          including_default_value_fields=True),
            )

            utils.copy_project_files(self.project_id, diffs)
            self.current_project_revision_id = revision.id

        res = {
            "action": "sync",
            "type": "status",
            "message": {
                "status": 200,
                "message": "Project files synchronized."
            }
        }
        return json.dumps(res)

    def commit(self, msg):
        # synchronize changes with Minio
        if not msg:
            res = {
                "action": "commit",
                "type": "status",
                "message": {
                    "status": 400,
                    "message": "msg cannot be empty, please provide a valid commit message."
                }
            }
        else:
            changes = self.watcher.get_state()
            if changes is not None:
                response = utils.commit_project(self.project_id, msg, self.author, changes)
                self.current_project_revision_id = response.id
                self.watcher.flush()
                data = {"revision": response.id}
                # save revision in config
                self.save_config(data)

            res = {
                "action": "commit",
                "type": "status",
                "message": {
                    "status": 200,
                    "message": "Committed changes."
                }
            }
            
        return json.dumps(res)

    def persist_data(self):
        # create dataset version
        for dataset_id, dataset_version, mount_output in self.datasets:
            if mount_output:
                dataset_path = os.path.join(config.ILYDE_WORKING_DIR, "datasets", "output",
                                            self.bucket_mappings[dataset_id]["name"])
                if os.listdir(dataset_path):
                    utils.create_dataset_version(dataset_id, self.bucket_mappings[dataset_id]["bucket"], self.author)

        res = {
            "action": "persist",
            "type": "status",
            "message": {
                "status": 200,
                "message": "All datasets are saved successfully."
            }
        }

        return json.dumps(res)

    def changes(self):
        changes = self.watcher.get_state()
        if changes is not None:
            res = {
                "action": "changes",
                "type": "workdir_changes",
                "message": {
                    "total": len(changes),
                    "changes": ["{} - {}".format(change.get("action"),
                                                 change.get("path")) for change in changes]
                }
            }
        else:
            res = {
                "action": "changes",
                "type": "workdir_changes",
                "message": {
                    "total": 0,
                    "changes": []
                }
            }
        return json.dumps(res)

    async def handler(self, websocket, path):
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "sync":
                await websocket.send(self.sync())
            elif data["action"] == "commit":
                await websocket.send(self.commit(data["message"]))
            elif data["action"] == "diff":
                await websocket.send(self.diff())
            elif data["action"] == "changes":
                await websocket.send(self.changes())
            elif data["action"] == "persist":
                await websocket.send(self.persist_data())
            else:
                logging.error("unsupported event: {}", data)


def serve(project, revision, author, datasets, bucket_mappings, watcher):
    agent = JobAgentSocket(project, revision, author, datasets, bucket_mappings, watcher)
    start_server = websockets.serve(agent.handler, "0.0.0.0", 6789)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
