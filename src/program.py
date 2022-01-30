import queue

import serial.tools.list_ports
import threading
from time import sleep

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
    def __init__(self, event, serial_handler):
        super().__init__(daemon=True)
        self.is_running: threading.Event = event
        self.serial: SerialHandler = serial_handler

    def run(self):
        self.is_running.set()
        while self.is_running.is_set():
            if not self.serial.is_running.is_set():
                sleep(0.1)
            self.serial.read()
        self.serial.disconnect()


class SerialHandler:
    def __init__(self):
        self.serial = serial.Serial()
        self.is_running = threading.Event()
        self.queue_in = queue.Queue()
        self.queue_out = queue.Queue()
        self.data = []
        self.buffer = ''
        self.counter = 0

    def connect(self, name):
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
        self.serial.close()
        return True

    def read(self):
        if not self.is_running.is_set():
            return
        buffer = self.serial.read(10)
        self.format(buffer)
        self.reorder()

    def write(self):
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


def main0():
    print('Running main0()\n')
    list_comports = serial.tools.list_ports.comports()
    for c in list_comports:
        print(c.device, type(c.device))
        print(c.description)
        print(c.hwid)
        print(c.location)
        print(c.name, type(c.name))
        print(c.pid)
        print(c.manufacturer)
        print(c.serial_number)
    if not len(list_comports):
        print(None)


def main1():
    print('Running main1()\n')
    list_comports = serial.tools.list_ports.comports()
    if not len(list_comports):
        return
    for p in list_comports:
        print(p.name)
    arduino = serial.Serial(list_comports[0].name)
    print(arduino.name)
    for _ in range(8):
        text = arduino.readline()
        print(text)
    arduino.close()


def main():
    print('Running main()\n')
    running = threading.Event()
    arduino = SerialHandler()
    thread = SerialThread(running, arduino)
    thread.start()
    success = thread.serial.connect('COM3')
    if not success:
        print('No COM3')
    sleep(4)
    running.clear()
    thread.join(1)
    q = arduino.queue_in
    for _ in range(8):
        if not q.empty():
            print(q.get())


if __name__ == '__main__':
    # main()
    main0()
    # main1()
