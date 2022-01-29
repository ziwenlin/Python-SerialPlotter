import queue

import serial.tools.list_ports
import threading


class SerialThread(threading.Thread):
    def __init__(self, event):
        super().__init__(daemon=True)
        self.is_running = event
        self.serial = SerialHandler()

    def run(self):
        self.is_running.set()
        while self.is_running.is_set():
            self.serial.read()
        self.serial.disconnect()


class SerialHandler:
    def __init__(self):
        self.arduino: serial.Serial
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
            return False
        self.arduino = serial.Serial(name)
        self.is_running.set()
        return True

    def disconnect(self):
        if not self.is_running.is_set():
            return
        self.arduino.close()
        self.is_running.clear()

    def read(self):
        if not self.is_running.is_set():
            return
        buffer = self.arduino.read(10)
        self.format(buffer)
        self.reorder()

    def write(self):
        if not self.is_running.is_set():
            return
        while not self.queue_out.empty():
            data = self.queue_out.get()
            self.arduino.write(data)

    def reorder(self):
        if not len(self.data):
            return
        data: str = self.data.pop(0)
        data: list = data.split(',')
        data: list = [float(d) for d in data]
        self.queue_in.put(data)

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
        print(c.device)
        print(c.description)
        print(c.hwid)
        print(c.location)
        print(c.name)
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
    is_running = threading.Event()
    thread = SerialThread(is_running)
    thread.start()
    success = thread.serial.connect('COM3')
    if not success:
        print('No COM3')
    sleep(4)
    is_running.clear()
    thread.join(1)
    for text in thread.serial.data[:8]:
        print(text)


if __name__ == '__main__':
    from time import sleep

    # main0()
    # sleep(1)
    # main1()
    # sleep(1)
    main()
    sleep(1)
