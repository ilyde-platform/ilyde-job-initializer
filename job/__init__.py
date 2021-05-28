# encoding: utf-8
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
import errno
import functools
import itertools
import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Watcher:

    def __init__(self, directory, log):
        self.observer = Observer()
        self.directory = directory
        self.log = log

    def run(self):
        event_handler = Handler(self.log, self.directory)
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def flush(self):
        try:
            with open(self.log, "w") as f:
                f.seek(0)
                f.truncate()

            return True
        except FileNotFoundError as e:
            return False

    def get_state(self):
        # retrieve all modifications
        try:
            with open(self.log, "r") as f:
                lines = f.readlines()
        except FileNotFoundError as e:
            return None

        if not len(lines):
            return None

        # parse file and get latest modifications
        lines = map(lambda line: line.replace("\n", "").split("%%"), lines)
        data = []
        for k, g in itertools.groupby(sorted(lines, key=lambda line: line[2]), lambda line: line[2]):

            if k.startswith('/ilyde/.Trash') or k.startswith('/ilyde/.ilyde') or '.ipynb_checkpoints' in k:
                continue

            groups = list(g)
            actions = [c[1] for c in groups]

            if "created" in actions and "deleted" in actions:
                continue

            if "modified" in actions and "created" in actions:
                data.append({'action': "created", 'path': k})
                continue

            obj = functools.reduce(lambda l1, l2: l1 if float(l1[0]) > float(l2[0]) else l2, groups)
            data.append({'action': obj[1], 'path': obj[2]})

        return data


class Handler(FileSystemEventHandler):

    def __init__(self, log, monitor_dir):
        super(Handler).__init__()
        self.log_file = log
        self.dirs_to_exclude = ["{}/{}".format(monitor_dir, "datasets"),
                                "{}/{}".format(monitor_dir, ".ilyde"),
                                "{}/{}".format(monitor_dir, ".vscode")]

    def _write_log(self, lines):
        if not os.path.exists(os.path.dirname(self.log_file)):
            try:
                os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(self.log_file, "a+") as f:
            f.writelines(lines)

    def _can_write(self, filename) -> bool:
        if any([filename.startswith(d) for d in self.dirs_to_exclude]):
            return False

        return True

    def on_created(self, event):

        if self._can_write(event.src_path) and not event.is_directory:
            line = "{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                           event=event.event_type,
                                                           path=event.src_path)
            self._write_log([line])

    def on_deleted(self, event):

        if self._can_write(event.src_path) and not event.is_directory:
            line = "{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                           event=event.event_type,
                                                           path=event.src_path)
            self._write_log([line])

    def on_modified(self, event):

        if self._can_write(event.src_path) and not event.is_directory:
            line = "{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                           event=event.event_type,
                                                           path=event.src_path)
            self._write_log([line])

    def on_moved(self, event):

        if self._can_write(event.src_path) and not event.is_directory:
            lines = ["{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                             event=event.event_type, path=event.src_path),
                     "{timestamp}%%deleted%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                             path=event.src_path)]
            self._write_log(lines)
