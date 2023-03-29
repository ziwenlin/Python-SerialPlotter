import threading
import unittest
from time import sleep

from SerialPlotter.device import SerialThread, SerialHandler, BufferConverter


class TestSerial(unittest.TestCase):

    def test_buffer_add(self):
        converter = BufferConverter()
        converter.add('This\tis\ra,string\n5454,353\n535\n')
        check_list = ['This\tis\ra,string\n', '5454,353\n', '535\n']
        self.assertListEqual(check_list, converter.buffer_lines)

    def test_buffer_update(self):
        converter = BufferConverter()
        converter.add('This\tis\ra,string\n5454,353\n535\n')

        check_list = ['Message: This\tis\ra,string\n']
        converter.update()
        self.assertEqual([], converter.data)
        self.assertEqual(check_list, converter.messages)

        check_list += ['Unknown: ' + str(b'5454,353\n')]
        converter.update()
        self.assertEqual([], converter.data)
        self.assertEqual(check_list, converter.messages)

        converter.update()
        self.assertEqual([[535.0]], converter.data)
        self.assertEqual(check_list, converter.messages)

    def test_buffer_converter_to_data(self):
        converter = BufferConverter()
        converter.convert_to_data('333\t222\r\n')
        check_list = [333.0, 222.0]
        self.assertListEqual(converter.data, [check_list])
        converter.convert_to_data('333\t222\r\n')
        self.assertListEqual([check_list, check_list], converter.data)

    def test_thread_start_exit(self):
        running = threading.Event()
        running.set()
        thread = SerialThread(running)
        thread.start()
        sleep(0.1)
        self.assertTrue(thread.is_alive(), "Thread did not start")
        sleep(0.1)
        running.clear()
        sleep(0.1)
        self.assertFalse(thread.is_alive(), "Thread did not close")
