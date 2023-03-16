import threading
from typing import List

from .program import SerialHandler, SerialThread

UPDATE_INTERVAL = 500


class ThreadInterface:
    serial_controller: SerialHandler

    def __init__(self):
        self.serial_controller = SerialHandler()

class ThreadManager:
    running: threading.Event
    threads: List[threading.Thread]

    def __init__(self):
        self.running = threading.Event()
        self.threads = []

    def start_threads(self):
        self.running.is_set()
        for thread in self.threads:
            thread.start()

    def stop_threads(self):
        self.running.clear()
        for thread in self.threads:
            thread.join(1)

    def exit_threads(self, max_tries=10):
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
