import threading
from time import sleep

import serial.tools.list_ports

from SerialPlotter.device import SerialHandler, SerialThread


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
