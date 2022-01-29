import threading
import unittest

from time import sleep
from program import SerialThread


class TestThreadingProgram(unittest.TestCase):

    def test_thread_exit(self):
        is_running = threading.Event()
        is_running.set()
        thread = SerialThread(is_running)
        thread.start()
        is_running.clear()
        sleep(0.1)
        self.assertFalse(thread.is_alive(), "Thread did not close")
