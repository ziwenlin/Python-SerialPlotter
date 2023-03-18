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

    def run(self):
        self.is_running.set()
        while self.is_running.is_set():
            if not self.serial.is_running.is_set():
                sleep(0.1)
            while self.serial.available() > 10:
                self.serial.read()
            self.serial.write()
            sleep(0.1)

        self.serial.disconnect()


class SerialInterface:
    """This is the view"""
    queues: Dict[str, List[queue.Queue]]

    def __init__(self):
        self.queues = {
            'in': [],
            'out': [],
            'raw': [],
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


class SerialHandler:
    """This is the model"""

    def __init__(self):
        self.serial = serial.Serial()
        self.is_running = threading.Event()
        self.queue_in = queue.Queue()
        self.queue_out = queue.Queue()
        self.data = []
        self.buffer = ''
        self.counter = 0
        self.debug = False

    def available(self):
        if self.debug:
            self.counter += 1
            sleep(0.2)
            return self.counter
        if not self.is_running.is_set():
            return 0
        return self.serial.inWaiting()

    def connect(self, name):
        if name == 'debug':
            self.debug = True
            self.is_running.set()
            return True
        for p in serial.tools.list_ports.comports():
            if p.name == name:
                break
        else:
            return None
        if self.is_running.is_set():
            return False
        self.serial = serial.Serial(name, timeout=0)
        self.is_running.set()
        return True

    def disconnect(self):
        if not self.is_running.is_set():
            return False
        self.is_running.clear()
        if self.debug:
            self.debug = False
            return True
        self.serial.close()
        return True

    def read(self):
        if self.debug:
            self.counter = 0
            self.queue_in.put([random.random() for _ in range(3)])
            return
        if not self.is_running.is_set():
            return
        buffer = self.serial.read(32)
        try:
            self.format(buffer)
            self.reorder()
        except:
            self.data = ''
            self.buffer = ''

    def write(self):
        if self.debug:
            while not self.queue_out.empty():
                data: str = self.queue_out.get()
                print(data)
            return
        if not self.is_running.is_set():
            return
        while not self.queue_out.empty():
            data: str = self.queue_out.get()
            self.serial.write(data.encode())

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
