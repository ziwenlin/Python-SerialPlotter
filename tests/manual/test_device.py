import threading
from time import sleep

import serial.tools.list_ports

from SerialPlotter.device import SerialThread


def print_serial_ports():
    print('Running print_serial_ports()\n')
    list_comports = serial.tools.list_ports.comports()
    for c in list_comports:
        print(
            c.name, type(c.name), '\n',
            c.device, type(c.device), '\n',
            c.manufacturer, c.pid, c.serial_number, c.location, '\n',
            c.description, '\n',
            c.hwid, '\n',
        )
    if not len(list_comports):
        print(None)


def print_incoming_data():
    print('Running print_incoming_data()\n')
    list_comports = serial.tools.list_ports.comports()
    if not len(list_comports):
        return
    for p in list_comports:
        print('Device:', p.device, 'Name:', p.name)
    arduino = serial.Serial(list_comports[1].name, timeout=1)
    print(arduino.name)
    for _ in range(8):
        text = arduino.readline()
        print(text)
    arduino.close()


def test_thread_connection():
    print('Running test_thread_connection()\n')
    running = threading.Event()
    thread = SerialThread(running)
    q = thread.interface.create_queue('in')
    thread.start()
    success = thread.serial.connect('COM3')
    if not success:
        print('No COM3')
    sleep(4)
    running.clear()
    thread.join(1)
    for _ in range(8):
        if not q.empty():
            print(q.get())


if __name__ == '__main__':
    print_serial_ports()
    print_incoming_data()
    test_thread_connection()
