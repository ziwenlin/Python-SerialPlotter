import tkinter as tk

from serial.tools.list_ports import comports

from interfacebuilder import make_base_frame, make_spaced_label, make_button, make_spacer, \
    make_updatable_label, InterfaceVariables, make_combobox, make_graph, make_thread, make_check_button, \
    make_named_spinbox


def build_interface():
    top = tk.Tk()
    interface = InterfaceVariables()
    panel_port_selector(top, interface)
    panel_graph_control(top, interface)
    panel_graph_view(top, interface)

    return top, interface

def panel_graph_control(base, interface:InterfaceVariables):
    frame = make_base_frame(base)
    make_spaced_label(frame, 'Configurator')
    make_check_button(frame, interface.tk_vars, 'Lock axis')
    make_check_button(frame, interface.tk_vars, 'Copy axis')

    make_spaced_label(frame, 'X-axis')
    interface.tk_vars['x min'] = make_named_spinbox(frame, 'Min')
    interface.tk_vars['x max'] = make_named_spinbox(frame, 'Max')
    make_spaced_label(frame, 'Y-axis')
    interface.tk_vars['y min'] = make_named_spinbox(frame, 'Min')
    interface.tk_vars['y max'] = make_named_spinbox(frame, 'Max')

    for i in range(20):
        make_check_button(frame, interface.tk_vars, f'graph{i}')


def panel_graph_view(base, interface: InterfaceVariables):
    frame = make_base_frame(base)
    frame.config(width=2000)
    graph = make_graph(frame)
    # interface.tk_data['graph'] = []

    def update():
        running = not interface.arduino.queue_in.empty()
        if interface.tk_vars.get('Lock axis').get() == True:
            try:
                x_min = float(interface.tk_vars.get('x min').get())
                x_max = float(interface.tk_vars.get('x max').get())
                y_min = float(interface.tk_vars.get('y min').get())
                y_max = float(interface.tk_vars.get('y max').get())
            except ValueError:
                return
            if x_min == x_max:
                x_min -= 1
            if y_min == y_max:
                y_min -= 1
            graph.plot.set_xlim(x_min, x_max)
            graph.plot.set_ylim(y_min, y_max)
        if interface.tk_vars.get('Copy axis').get() == True:
            x_min, x_max = graph.plot.get_xlim()
            y_min, y_max = graph.plot.get_ylim()
            interface.tk_vars.get('x min').set(f'{x_min:.2f}')
            interface.tk_vars.get('x max').set(f'{x_max:.2f}')
            interface.tk_vars.get('y min').set(f'{y_min:.2f}')
            interface.tk_vars.get('y max').set(f'{y_max:.2f}')
        if not running:
            return
        graph_I: dict = {}
        for i in range(20):
            state = interface.tk_vars.get(f'graph{i}').get() == True
            graph_I.update({i: state})
        while not interface.arduino.queue_in.empty():
            serial_data = interface.arduino.queue_in.get()
            for index, value in enumerate(serial_data):
                try:
                    interface.graph_data[index] += [value]
                except KeyError:
                    interface.graph_data[index] = [value]
                    # interface.tk_data['graph'].append(index)
        graph_data = {}
        for key, values in interface.graph_data.items():
            if graph_I[key] == True:
                graph_data.update({key: values[-500:]})
        graph.update(graph_data)

    def thread():
        from time import sleep
        sleep(1)
        while interface.running.is_set():
            update()
            sleep(0.1)

    make_thread(thread, interface)


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
        interface.tk_vars.get('success').set(success)

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
        interface.tk_vars.get('success').set(success)

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
        interface.tk_vars.get('success').set(success)

    def refresh_command():
        text = ''
        ports = []
        for port in comports():
            name = str(port.device)
            ports += [name]
            text += name + '\n'
        if len(ports) == 0:
            text += 'None available'
            ports += ['None']
        interface.tk_data['port'] = ports
        interface.tk_vars.get('ports').set(text)

    frame = make_base_frame(base)
    make_spaced_label(frame, 'Configurator')

    make_spacer(frame, 10)
    make_spaced_label(frame, 'Selectable ports:')
    make_updatable_label(frame, interface.tk_vars, 'ports')

    make_spacer(frame, 10)
    combobox = make_combobox(frame, interface.tk_data, 'port')
    make_updatable_label(frame, interface.tk_vars, 'success')
    make_button(frame, refresh_command, 'Refresh')
    make_button(frame, connect_command, 'Connect')
    make_button(frame, disconnect_command, 'Disconnect')
    make_button(frame, reconnect_command, 'Reconnect')


def main():
    root, interface = build_interface()
    interface.thread_serial.start()
    root.mainloop()
    interface.running.clear()
    for thread in interface.threads:
        if thread.isDaemon():
            thread.join()


if __name__ == '__main__':
    main()
