import threading
from typing import List

from .program import SerialHandler, SerialThread

UPDATE_INTERVAL = 500


class ThreadManager:
    running: threading.Event
    threads: List[threading.Thread]

    def __init__(self):
        self.running = threading.Event()
        self.threads = []

    def add_thread(self, thread: threading.Thread):
        if self.running.is_set():
            thread.start()
        self.threads.append(thread)

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


class ThreadInterface:
    thread_manager: ThreadManager
    serial_controller: SerialHandler

    def __init__(self):
        self.thread_manager = ThreadManager()
        self.serial_controller = SerialHandler()
        self.thread_manager.add_thread(SerialThread(
            self.thread_manager.running,
            self.serial_controller))
