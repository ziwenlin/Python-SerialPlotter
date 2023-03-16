import threading
from typing import List

from .program import SerialHandler, SerialThread

UPDATE_INTERVAL = 500


class InterfaceVariables:
    arduino = SerialHandler()


class ThreadManager:
    running = threading.Event()
    threads: List[threading.Thread]

    def __init__(self):
        thread_serial = SerialThread(self.running, InterfaceVariables.arduino)
        self.threads = [thread_serial]

    def start_threads(self):
        self.running.is_set()
        for thread in self.threads:
            thread.start()

    def stop_threads(self):
        self.running.clear()
        tries = 1
        # print('Active threads now:', threading.active_count())
        while threading.active_count() > 1:
            for thread in self.threads:
                thread.join(2)
                if tries > 2 and thread.is_alive():
                    print('Stuborn thread:', thread.name)
            if tries > 3:
                print('Force close python')
                break
            else:
                tries += 1
