import threading
import unittest

from time import sleep
from program import SerialThread, SerialHandler


class TestThreadingProgram(unittest.TestCase):

    def test_serial_handler_format(self):
        serial = SerialHandler()
        serial.format(b'This\tis\ra,string\n5454353\n535\n')
        check_list = ['This,isa,string', '5454353']
        self.assertListEqual(serial.data, check_list, "Serial formatter did something unexpected")

    def test_serial_handler_queue(self):
        serial = SerialHandler()
        serial.format(b'This\tis\ra,string\n5454,353\n535\n')
        self.assertRaises(ValueError, serial.reorder)
        serial.reorder()
        self.assertFalse(serial.queue_in.empty())
        self.assertEqual(serial.queue_in.get(), [5454.0, 353.0])

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
