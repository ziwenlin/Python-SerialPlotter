import queue
import threading
import time
from typing import List

from SerialPlotter import files


class StorageInterace:
    queue_data: queue.Queue
    queue_status: queue.Queue
    queue_command: queue.Queue

    def __init__(self):
        self.queue_data = queue.Queue()
        self.queue_status = queue.Queue()
        self.queue_command = queue.Queue()


class StorageHolder:
    recorder_data: List[List[float]]
    backup_data: List[List[float]]

    def __init__(self):
        self.backup_data = []
        self.backup_size = 500
        self.recorder_data = []
        self.recorder_size = 500
        self.is_recording = False
        self.is_auto_save = False
        self.file_name = 'Unnamed'
        self.delimiter = ';'
        self.decimal = ','

    def add(self, data):
        if self.is_recording is True:
            self.recorder_data.append(data)
        self.backup_data.append(data)

    def update(self):
        self.update_backup_status()
        self.update_recorder_status()

    def update_recorder_status(self):
        if len(self.recorder_data) < self.recorder_size:
            return
        if self.is_auto_save is False:
            return
        self.save_recorder_data()

    def update_backup_status(self):
        if len(self.backup_data) < self.backup_size:
            return
        self.save_backup_data()

    def save_recorder_data(self):
        if not len(self.recorder_data) > 0:
            return
        if not len(self.file_name) > 0:
            self.file_name = 'Unnamed'
        files.CSV_DELIMITER = self.delimiter
        files.csv_save_append(self.file_name, self.recorder_data)
        self.recorder_data.clear()

    def save_backup_data(self):
        if not len(self.backup_data) > 0:
            return
        files.CSV_DELIMITER = self.delimiter
        files.csv_save_auto(self.backup_data)
        self.backup_data.clear()


class StorageThread(threading.Thread):
    is_running: threading.Event

    def __init__(self, event):
        super().__init__(daemon=False, name='Storage')
        self.is_running = event
        self.interface = StorageInterace()
        self.storage = StorageHolder()

    def run(self):
        self.is_running.set()
        while self.is_running.is_set():
            self.update_request_queues()
            self.storage.update()
            time.sleep(0.2)
        self.exit()

    def exit(self):
        if self.storage.is_auto_save is True:
            self.storage.save_recorder_data()
        self.storage.save_backup_data()

    def update_request_queues(self):
        while not self.interface.queue_data.empty():
            data = self.interface.queue_data.get()
            self.storage.add(data)
        while not self.interface.queue_command.empty():
            command = self.interface.queue_command.get()
            self.process_command(command)

    def process_command(self, command: str):
        cmd, *arg = command.split(' ')
        if cmd == 'delimiter':
            message = self.process_delimiter(arg[0])
        elif cmd == 'recorder':
            message = self.process_recorder(arg[0])
        elif cmd == 'auto_save':
            message = self.process_auto_save(arg[0])
        elif cmd == 'file_name':
            message = self.process_file_name(arg[0])
        else:
            message = f'Unknown command: {command}'
        self.interface.queue_status.put(message)

    def process_file_name(self, file_name):
        self.storage.file_name = file_name
        message = f'File name changed to {file_name}.csv '
        return message

    def process_recorder(self, subcommand: str):
        if subcommand == 'start':
            self.storage.is_recording = True
            return "Recorder started"
        elif subcommand == 'pause':
            self.storage.is_recording = False
            return 'Recorder paused'
        elif subcommand == 'save':
            self.storage.save_recorder_data()
            return 'Recorder data stored'
        return 'Unknown subcommand'

    def process_delimiter(self, delimiter: str):
        self.storage.delimiter = delimiter
        return 'Delimiter set to ' + str(delimiter.encode())

    def process_auto_save(self, state: str):
        if state == 'enable':
            self.storage.is_auto_save = True
            return 'Auto save enabled'
        elif state == 'disable':
            self.storage.is_auto_save = False
            return 'Auto save disabled'
        return 'Unknown state'
