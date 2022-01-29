import threading
import unittest

from time import sleep
from program import SerialThread, SerialHandler


class TestThreadingProgram(unittest.TestCase):

    def test_thread_start_exit(self):
        serial = SerialHandler()
        running = threading.Event()
        running.set()
        thread = SerialThread(running, serial)
        thread.start()
        self.assertTrue(thread.is_alive(), "Thread did not start")
        sleep(0.1)
        running.clear()
        sleep(0.1)
        self.assertFalse(thread.is_alive(), "Thread did not close")
