# encoding: utf-8
import functools
import itertools
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
            obj = functools.reduce(
                lambda l1, l2: l1 if float(l1[0]) > float(l2[0]) else l2,
                g)
            data.append({'action': obj[1], 'path': obj[2]})

        return data


class Handler(FileSystemEventHandler):

    def __init__(self, log, monitor_dir):
        super(Handler).__init__()
        self.log_file = log
        self.dir_to_exclude = "{}/{}".format(monitor_dir, "datasets")
        # create log file

    def on_created(self, event):

        if not event.src_path.startswith(self.dir_to_exclude) and not event.is_directory:
            line = "{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                           event=event.event_type,
                                                           path=event.src_path)
            with open(self.log_file, "a+") as f:
                f.writelines([line])

    def on_deleted(self, event):

        if not event.src_path.startswith(self.dir_to_exclude) and not event.is_directory:
            line = "{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                           event=event.event_type,
                                                           path=event.src_path)
            with open(self.log_file, "a+") as f:
                f.writelines([line])

    def on_modified(self, event):

        if not event.src_path.startswith(self.dir_to_exclude) and not event.is_directory:
            line = "{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                           event=event.event_type,
                                                           path=event.src_path)
            with open(self.log_file, "a+") as f:
                f.writelines([line])

    def on_moved(self, event):

        if not event.src_path.startswith(self.dir_to_exclude) and not event.is_directory:
            lines = ["{timestamp}%%{event}%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                              event=event.event_type,
                                                              path=event.src_path),
                     "{timestamp}%%deleted%%{path}\n".format(timestamp=time.mktime(time.localtime()),
                                                             path=event.src_path)]

            with open(self.log_file, "a+") as f:
                f.writelines(lines)
