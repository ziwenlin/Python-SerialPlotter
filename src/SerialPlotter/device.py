import queue
import random
import threading
from time import sleep
from typing import List, Dict

import serial.tools.list_ports

test_count = 0


def test_print():
    global test_count
    test_count += 1
    if test_count % 100:
        print(test_count % 10, end='')
    else:
        print(test_count % 10)
        test_count = 0


class BufferConverter:
    """This is another model"""

    def __init__(self):
        self.delimiter = '\t'
        self.new_line = '\n'
        self.carriage = '\r'
        self.decimal = '.'
        self.negative = '-'

        self.messages = []
        self.lines = []
        self.data = []

        self.buffer_lines = []
        self.buffer_text = ''

    def add(self, buffer: str):
        for char in buffer:
            self.buffer_text += char
            if char in self.new_line:
                self.collect_buffer()

    def available(self):
        return len(self.buffer_lines)

    def update(self):
        if not len(self.buffer_lines) > 0:
            return False
        line = self.buffer_lines.pop(0)
        status = self.analyse_line(line)

        if status == 'data':
            try:
                self.convert_to_data(line)
            except ValueError:
                self.convert_to_invalid(line)
        elif status == 'message':
            self.convert_to_message(line)
        elif status == 'unknown':
            self.convert_to_unknown(line)
        else:
            self.convert_to_invalid(line)
        self.lines.append(line)
        return True

    def convert_to_message(self, line_text):
        text = 'Message: ' + line_text
        self.messages.append(text)

    def convert_to_unknown(self, line_text: str):
        text = 'Unknown: ' + str(line_text.encode())
        self.messages.append(text)

    def convert_to_invalid(self, line_text: str):
        text = 'Invalid: ' + str(line_text.encode())
        self.messages.append(text)

    def convert_to_data(self, line_text):
        # Convert to normal text without newline
        text: str = line_text[:-1]
        text_list = text.split(self.delimiter)
        value_list = [float(text_value) for text_value in text_list]
        self.data.append(value_list)
        return value_list

    def collect_buffer(self):
        buffer = self.buffer_text
        self.buffer_lines.append(buffer)
        self.buffer_text = ''
        return buffer

    def analyse_line(self, line_text: str):
        numbers = alphabets = symbols = unknown = 0
        for char in line_text:
            if char.isnumeric():
                numbers += 1
            elif char.isalpha():
                alphabets += 1
            elif char in self.delimiter:
                symbols += 1
            elif char in self.new_line:
                symbols += 1
            elif char in self.carriage:
                symbols += 1
            elif char in self.decimal:
                symbols += 1
            elif char in self.negative:
                symbols += 1
            else:
                unknown += 1
                # print(char.encode())
        # print(numbers, misc, alphabets, unknown)

        # Determine what the type of line_text is
        if alphabets > 0:
            return 'message'
        if unknown > 0:
            return 'unknown'
        if numbers > 0:
            return 'data'
        return 'invalid'


class SerialThread(threading.Thread):
    """This is the controller"""
    is_running: threading.Event

    def __init__(self, event):
        super().__init__(daemon=False, name='Serial')
        self.is_running: threading.Event = event
        self.serial: SerialHandler = SerialHandler()
        self.interface: SerialInterface = SerialInterface()
        self.converter: BufferConverter = BufferConverter()

    def run(self):
        self.is_running.set()
        while self.is_running.is_set():
            self.update_request_queues()
            self.update_response_queues()
            if not self.serial.is_connected.is_set():
                sleep(0.1)
                continue
            while self.serial.available() > 0:
                buffer = self.serial.read()
                self.converter.add(buffer)
            while self.converter.available() > 0:
                self.converter.update()
            for message in self.interface.get_items('out'):
                self.serial.write(message)
            sleep(0.001)
        # Close serial connection when the main program wants to exit
        self.serial.disconnect()

    def update_response_queues(self):
        while len(self.converter.messages) > 0:
            message = self.converter.messages.pop(0)
            self.interface.queue_item('text', message)
        while len(self.converter.data) > 0:
            data = self.converter.data.pop(0)
            self.interface.queue_item('data', data)
        while len(self.converter.lines) > 0:
            line = self.converter.lines.pop(0)
            self.interface.queue_item('in', line)

    def update_request_queues(self):
        items: List[str] = self.interface.get_items('command')
        for command in items:
            self.process_command(command)

    def process_command(self, command: str):
        cmd, *arg = command.split(' ')
        if cmd == 'disconnect':
            message = self.process_disconnect()
        elif cmd == 'reconnect':
            message = self.process_reconnect()
        elif cmd == 'connect':
            message = self.process_connect(arg[0])
        else:
            message = f'Unknown command: {command}'
        self.interface.queue_item('status', message)

    def process_connect(self, name):
        try:
            status = self.serial.connect(name)
        except serial.SerialException as e:
            return str(e)
        if status:
            message = f'Successfully connected to device {name}'
        elif self.serial.is_connected.is_set():
            message = 'There is already an connection, please disconnect'
        else:
            message = f'Could not connect to device {name}'
        return message

    def process_reconnect(self):
        name = self.serial.serial.name
        status = self.serial.disconnect()
        status *= self.serial.connect(name)
        if status:
            message = f'Successfully reconnected'
        else:
            message = 'Reconnecting failed: There was no connection'
        return message

    def process_disconnect(self):
        status = self.serial.disconnect()
        if status:
            message = 'Successfully disconnected'
        else:
            message = 'Disconnecting failed: There was no connection'
        return message


class SerialInterface:
    """This is the view"""
    queues: Dict[str, List[queue.Queue]]

    def __init__(self):
        self.queues = {
            'in': [],  # Messages that are straight from the serial connection
            'out': [],  # Messages that needs to be sent to the serial connection
            'data': [],  # Messages converted to usable data
            'text': [],  # Messages which contains text instead of data
            'status': [],  # Status messages from the controller
            'command': [],  # Command messages to the controller
        }

    def create_queue(self, name: str, max_size=1000):
        if name not in self.queues:
            return
        new_queue = queue.Queue(max_size)
        self.queues[name].append(new_queue)
        return new_queue

    def queue_item(self, name: str, item):
        if name not in self.queues:
            return
        current_queues = self.queues[name]
        for q in current_queues:
            if q.full():
                continue
            q.put(item, False)

    def get_items(self, name: str):
        if name not in self.queues:
            return []
        items = []
        queue_list = self.queues[name]
        for current_queue in queue_list:
            while not current_queue.empty():
                item = current_queue.get()
                items.append(item)
        return items


class SerialHandler:
    """This is the model"""

    def __init__(self):
        self.serial = serial.Serial()
        self.is_connected = threading.Event()
        self.is_debug = False
        self.time_debug = 0

    def available(self):
        """
        Gets the current amount of bytes in the input buffer.

        :return: Amount of bytes
        """
        if not self.is_connected.is_set():
            return 0
        if self.is_debug is True:
            self.time_debug += 1
            return self.time_debug - 3
        return self.serial.inWaiting()

    def connect(self, name):
        """
        Connects the application to a serial connection of a device.
        Returns True when the connection is established and
        False when the connection is not found or cannot be made.

        :param name: Name of the device
        :return: True or False
        """
        if self.is_connected.is_set():
            return False
        if name == 'debug':
            self.is_debug = True
            self.is_connected.set()
            return True
        for p in serial.tools.list_ports.comports():
            if p.device == name:
                break
        else:
            return False
        self.serial = serial.Serial(name, timeout=0.1)
        self.is_connected.set()
        return True

    def disconnect(self):
        """
        Disconnects the application from a serial connection of a device.
        Returns True when the connection is closed and
        False by no connection.

        :return: True or False
        """
        if not self.is_connected.is_set():
            return False
        self.is_connected.clear()
        if self.is_debug:
            self.is_debug = False
            return True
        self.serial.close()
        return True

    def read(self):
        """
        Reads the input buffer and returns its contents

        :return: Bytes in the buffer
        """
        if not self.is_connected.is_set():
            return
        if self.is_debug:
            self.time_debug = 0
            rand = random.Random()
            return f'{rand.random()}\t{rand.random()}\t{rand.random()}\n'
        buffer = self.serial.read(32)
        try:
            decode = buffer.decode()
        except UnicodeError:
            return ''
        return decode

    def write(self, message: str):
        """
        Writes the message to the output buffer.

        :param message: Message to the device
        """
        if not self.is_connected.is_set():
            return
        if self.is_debug:
            print(message)
            return
        self.serial.write(message.encode())
