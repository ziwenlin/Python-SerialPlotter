import tkinter as tk
from typing import List

import numpy as np

from interfacebuilder import make_base_frame, make_spaced_label, make_labeled_entry, make_button, make_spacer, \
    make_updateable_label, InterfaceVariables, make_combobox, make_graph
from serial.tools.list_ports import comports


def build_interface():
    top = tk.Tk()
    interface = InterfaceVariables()
    panel_port_selector(top, interface)
    panel_graph_view(top, interface)

    return top, interface


def panel_graph_view(base, interface: InterfaceVariables):
    frame = make_base_frame(base)
    graph = make_graph(frame)

    def update():
        while not interface.arduino.queue_in.empty():
            serial_data = interface.arduino.queue_in.get()
            for index, value in enumerate(serial_data):
                try:
                    interface.graph_data[index] += [value]
                except KeyError:
                    interface.graph_data[index] = [value]
        graph_data = {key: values[-500:] for key, values in interface.graph_data.items()}
        if graph_data.get(0):
            graph.ax.set_ylim(0, 100)
            graph.ax.set_xlim(0, 500)
        graph.update(graph_data)
        frame.after(100, update)

    # frame.after(100, update)


def panel_port_selector(base, interface: InterfaceVariables):
    def connect_command():
        arduino = interface.arduino
        port = combobox.get()
        success = arduino.connect(port)
        if success is True:
            success = 'Connected'
        elif success is False:
            success = 'Already connected'
        else:
            success = 'Not connected'
        # print(f'Port {port}: {success}')
        interface.tk_data.get('success').set(success)

    def disconnect_command():
        arduino = interface.arduino
        port = arduino.serial.name
        success = arduino.disconnect()
        if success is True:
            success = 'Disconnected'
        elif success is False:
            success = 'Not connected'
        else:  # This line should/will never happen
            success = 'Fatal error'
        # print(f'Port {port}: {success}')
        interface.tk_data.get('success').set(success)

    def reconnect_command():
        arduino = interface.arduino
        port = arduino.serial.name
        success1 = arduino.disconnect()
        success2 = arduino.connect(port)
        if success1 and success2 is True:
            success = 'Reconnected'
        elif success1 and success2 is False:
            success = 'Connected'
        else:
            success = 'Not connected'
        # print(f'Port {port}: {success}')
        interface.tk_data.get('success').set(success)

    def refresh_command():
        text = ''
        ports = []
        for port in comports():
            name = str(port.device)
            ports += [name]
            text += name + '\n'
        if not len(ports):
            text += 'None available'
        interface.serial_data['port'] = ports
        interface.tk_data.get('ports').set(text)

    frame = make_base_frame(base)
    make_spaced_label(frame, 'Configurator')

    make_spacer(frame, 10)
    make_spaced_label(frame, 'Selectable ports:')
    make_updateable_label(frame, interface.tk_data, 'ports')

    make_spacer(frame, 10)
    combobox = make_combobox(frame, interface.tk_data, 'port')
    make_updateable_label(frame, interface.tk_data, 'success')
    make_button(frame, refresh_command, 'Refresh')
    make_button(frame, connect_command, 'Connect')
    make_button(frame, disconnect_command, 'Disconnect')
    make_button(frame, reconnect_command, 'Reconnect')


def main():
    root, interface = build_interface()
    interface.thread.start()
    root.mainloop()
    interface.running.clear()
    interface.thread.join()


if __name__ == '__main__':
    main()
