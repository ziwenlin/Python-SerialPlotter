import threading
from typing import List, Dict

from .program import SerialHandler, SerialThread

UPDATE_INTERVAL = 500


class TaskManager:
    running: threading.Event
    threads: List[threading.Thread]

    def __init__(self):
        self.running = threading.Event()
        self.threads = []

    def add(self, thread: threading.Thread):
        if self.running.is_set():
            thread.start()
        self.threads.append(thread)

    def start(self):
        self.running.is_set()
        for thread in self.threads:
            thread.start()

    def stop(self):
        self.running.clear()
        for thread in self.threads:
            thread.join(1)

    def exit(self, max_tries=10):
        tries = 1
        while threading.active_count() > 1:
            for thread in self.threads:
                if not thread.is_alive():
                    continue
                thread.join(1)
                if tries < max_tries:
                    continue
                print('Stuborn thread:', thread.name)
            if tries > max_tries:
                print('Force close python')
                break
            tries += 1
        print('Active threads:', threading.active_count())


class TaskInterface:
    tasks_manager: TaskManager
    serial_controller: SerialHandler
    application_settings: Dict[str, any]

    def __init__(self):
        self.tasks_manager = TaskManager()
        self.application_settings = {}
        thread = SerialThread(self.tasks_manager.running)
        self.serial_controller = thread.serial
        self.tasks_manager.add(thread)
