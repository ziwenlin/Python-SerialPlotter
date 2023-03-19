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


class SerialThread(threading.Thread):
    """This is the controller"""
    is_running: threading.Event

    def __init__(self, event):
        super().__init__(daemon=False, name='Serial reader thread')
        self.is_running: threading.Event = event
        self.serial: SerialHandler = SerialHandler()
        self.interface: SerialInterface = SerialInterface()

    def run(self):
        self.is_running.set()
        while self.is_running.is_set():
            self.update_request_queues()
            if not self.serial.is_connected.is_set():
                sleep(0.1)
                continue
            # while self.serial.available() > 10:
            #     self.serial.read()
            # self.serial.write()
            sleep(0.1)

        self.serial.disconnect()

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
        status = self.serial.connect(name)
        if status:
            message = f'Succesfully connected to device {name}'
        else:
            message = f'Could not connect to device {name}'
        return message

    def process_reconnect(self):
        name = self.serial.serial.name
        status = self.serial.disconnect()
        status *= self.serial.connect(name)
        if status:
            message = f'Succesfully reconnected'
        else:
            message = 'There was no connection'
        return message

    def process_disconnect(self):
        status = self.serial.disconnect()
        if status:
            message = 'Succesfully disconnected'
        else:
            message = 'There was no connection'
        return message


class SerialInterface:
    """This is the view"""
    queues: Dict[str, List[queue.Queue]]

    def __init__(self):
        self.queues = {
            'in': [],  # Messages that are straight from the serial connection
            'out': [],  # Messages that needs to be sent to the serial connection
            'data': [],  # Messages converted to usable data
            'text': [],  # Messages which cannot be converted
            'status': [],  # Status messages from the controller
            'command': [],  # Command messages to the controller
        }

    def create_queue(self, name: str, max_size=100):
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

    def available(self):
        """
        Gets the current amount of bytes in the input buffer.

        :return: Amount of bytes
        """
        if not self.is_connected.is_set():
            return 0
        if self.is_debug:
            randint = random.Random().randint(0, 20)
            sleep(0.2)
            return randint
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
            rand = random.Random()
            return f'{rand.random()}\t{rand.random()}\t{rand.random()}\n'
        buffer = self.serial.read(32)
        return buffer.decode()

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

    def reorder(self):
        if not len(self.data):
            return
        data: str = self.data.pop(0)
        data: list = data.split(',')
        if len(data) < 3:
            return
        try:
            data: list = [float(d) for d in data]
            self.queue_in.put(data)
        except ValueError:
            return

    def format(self, buffer: bytes):
        for char in buffer.decode('utf-8'):
            if char in '\n':
                if len(self.buffer) > 5:
                    self.data.append(self.buffer)
                self.buffer = ''
                continue
            if char in '\0\r':
                continue
            if char in '\t':
                char = ','
            self.buffer += char
