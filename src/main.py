import tkinter as tk
from queue import Queue

from serial.tools.list_ports import comports

from filehandler import csv_save_auto, csv_save_append, csv_save_create
from interfacebuilder import make_base_frame, make_spaced_label, make_button, make_spacer, \
    make_updatable_label, InterfaceVariables, make_combobox, make_graph, make_thread, make_check_button, \
    make_named_spinbox, make_labeled_entry


def build_interface():
    top = tk.Tk()
    interface = InterfaceVariables()
    panel_port_selector(top, interface)
    panel_save_control(top, interface)
    panel_graph_control(top, interface)
    panel_graph_filter(top, interface)
    panel_graph_view(top, interface)

    return top, interface


def build_thread_interface(graph, interface: InterfaceVariables):
    from time import sleep
    filter_state = interface.graph_data['state']
    graph_filters = interface.tk_data.get('graph')
    tk_vars = interface.tk_vars

    def interface_manager():
        while interface.running.is_set():
            sleep(0.4)
            if not interface.running.is_set():
                return
            if interface.tk_vars.get('Lock axis').get() == 1:
                try:
                    x_min = float(tk_vars.get('x min').get())
                    x_max = float(tk_vars.get('x max').get())
                    y_min = float(tk_vars.get('y min').get())
                    y_max = float(tk_vars.get('y max').get())
                except ValueError:
                    continue
                if x_min == x_max:
                    x_min -= 1
                if y_min == y_max:
                    y_min -= 1
                graph.plot.set_xlim(x_min, x_max)
                graph.plot.set_ylim(y_min, y_max)
            if not interface.running.is_set():
                return
            if interface.tk_vars.get('Copy axis').get() == 1:
                x_min, x_max = graph.plot.get_xlim()
                y_min, y_max = graph.plot.get_ylim()
                tk_vars.get('x min').set(f'{x_min:.2f}')
                tk_vars.get('x max').set(f'{x_max:.2f}')
                tk_vars.get('y min').set(f'{y_min:.2f}')
                tk_vars.get('y max').set(f'{y_max:.2f}')
            if not interface.running.is_set():
                return
            for i, filter in enumerate(graph_filters):
                state = interface.tk_vars.get(filter).get() == 1
                filter_state.update({i: state})

    return interface_manager


def build_thread_graph(graph, interface: InterfaceVariables):
    from time import sleep
    csv_queue: Queue = interface.graph_data['auto csv']
    filter_state: dict = interface.graph_data['state']
    data: list = []
    queue = interface.arduino.queue_in

    def get_queue_data():
        while not queue.empty():
            serial_data = queue.get()
            for index, value in enumerate(serial_data):
                try:
                    data[index].append(value)
                except IndexError:
                    data.append([value])
            csv_queue.put(serial_data)

    def clean_up_data():
        if len(data) > 1000:
            del data[:500]

    def get_graph_data():
        graph_data: dict = {}
        for index, values in enumerate(data):
            if index in filter_state and filter_state[index] is True:
                graph_data.update({index: values[-200:]})
        return graph_data

    def serial_graph():
        while interface.running.is_set():
            if queue.empty():
                sleep(0.5)
                continue
            get_queue_data()
            clean_up_data()
            graph.update(get_graph_data())
            sleep(0.1)

    return serial_graph


def build_thread_csv(trigger: dict, interface: InterfaceVariables):
    from time import sleep
    auto_queue: Queue = interface.graph_data['auto csv']
    record_data: list = interface.graph_data['record csv']
    auto_data = []
    auto_save_var = interface.tk_vars['Auto save']

    def get_queue_data():
        record: bool = trigger['start']
        while not auto_queue.empty():
            serial_data = auto_queue.get()
            if record:
                record_data.append(serial_data)
            auto_data.append(serial_data)

    def auto_save_data():
        if len(auto_data) < 1000:
            return
        record: bool = trigger['start']
        if record and auto_save_var.get() == 1:
            name = trigger['name']
            csv_save_append(name, record_data)
            record_data.clear()
        csv_save_auto(auto_data)
        auto_data.clear()

    def csv_manager():
        while interface.running.is_set():
            if auto_queue.empty():
                sleep(0.5)
                continue
            get_queue_data()
            auto_save_data()
            sleep(0.1)
        record: bool = trigger['start']
        if record or auto_save_var.get() == 1:
            name = trigger['name']
            csv_save_append(name, record_data)
            record_data.clear()
        csv_save_auto(auto_data)
        auto_data.clear()

    return csv_manager


def panel_graph_control(base, interface: InterfaceVariables):
    frame = make_base_frame(base)
    make_spacer(frame, 2)
    make_spaced_label(frame, 'Configurator')
    make_check_button(frame, interface.tk_vars, 'Lock axis')
    make_check_button(frame, interface.tk_vars, 'Copy axis')

    make_spaced_label(frame, 'X-axis')
    interface.tk_vars['x min'] = make_named_spinbox(frame, 'Min')
    interface.tk_vars['x max'] = make_named_spinbox(frame, 'Max')
    make_spaced_label(frame, 'Y-axis')
    interface.tk_vars['y min'] = make_named_spinbox(frame, 'Min')
    interface.tk_vars['y max'] = make_named_spinbox(frame, 'Max')


def panel_graph_filter(base, interface: InterfaceVariables):
    interface.tk_data['graph'] = button_list = [
        'Pressure raw', 'Pressure filtered', 'Pressure average',
        'Pressure differential', 'Pressure filtered - average',
        'Pressure raw - average', 'Breath BPM', 'Breath BPM filtered',
        'Breath BPM smooth', 'Breath peak detection',
        'Heart beat signal', 'Heart beat peak', 'Heart beat BPM'
    ]

    frame = make_base_frame(base)
    make_spacer(frame, 2)
    make_spaced_label(frame, 'Graph line filters:')
    for name in button_list:
        make_check_button(frame, interface.tk_vars, name)
    interface.graph_data['state'] = {}


def panel_graph_view(base, interface: InterfaceVariables):
    frame = make_base_frame(base)
    frame.config(width=2000)
    graph = make_graph(frame)

    make_thread(build_thread_graph(graph, interface), interface, 'Serial graph')
    make_thread(build_thread_interface(graph, interface), interface, 'Interface manager')


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
            text += 'None available\n'
            ports += ['None']
        interface.tk_data['port'] = ports
        interface.tk_vars.get('ports').set(text)

    def send_command():
        data = entry.get()
        entry.delete(0, tk.END)
        interface.arduino.queue_out.put(data)

    frame = make_base_frame(base)
    make_spacer(frame, 2)
    make_spaced_label(frame, 'Selectable ports:')
    make_updatable_label(frame, interface.tk_vars, 'ports')
    interface.tk_vars.get('ports').set('Please refresh list\n')

    make_spacer(frame, 20)  # Give some space for those dangerous buttons
    make_updatable_label(frame, interface.tk_vars, 'success')
    combobox = make_combobox(frame, interface.tk_data, 'port')
    make_button(frame, refresh_command, 'Refresh')
    make_button(frame, connect_command, 'Connect')
    make_button(frame, disconnect_command, 'Disconnect')
    make_button(frame, reconnect_command, 'Reconnect')

    make_spacer(frame, 20)  # Give some space for those dangerous buttons
    entry = make_labeled_entry(frame, 'Send serial:')
    make_button(frame, send_command, 'Send')
    make_spacer(frame, 20)  # Give some space for those dangerous buttons


def panel_save_control(base, interface: InterfaceVariables):
    def save_command():
        record_data = interface.graph_data['record csv']
        auto_save_var = interface.tk_vars['Auto save']
        file_append_var = interface.tk_vars['File append']
        file_overwrite_var = interface.tk_vars['File overwrite']
        name = entry.get()
        if auto_save_var.get() == 1:
            return
        elif file_append_var.get() == 1:
            success = csv_save_append(name, record_data)
        elif file_overwrite_var.get() == 1:
            success = csv_save_create(name, record_data)
        else:
            success = csv_save_create(name, record_data)
        if auto_save_var.get() == 0:
            record_data.clear()
        if success is True:
            success = f'Saved data to {name}.csv'
        elif success is False:
            success = f'Could not save data to {name}.csv'
        else: # Fatal error
            success = f'Something went wrong with {name}.csv'
        interface.tk_vars.get('saving').set(success)

    def start_command():
        trigger['start'] = True
        interface.tk_vars.get('saving').set('Started recording')

    def pause_command():
        trigger['start'] = False
        interface.tk_vars.get('saving').set('Paused recording')

    frame = make_base_frame(base)
    make_spacer(frame, 2)
    entry = make_labeled_entry(frame, 'File name:')
    make_spaced_label(frame, 'Recording:')
    make_button(frame, start_command, 'Start')
    make_button(frame, pause_command, 'Pause')
    make_button(frame, save_command, 'Save')
    make_updatable_label(frame, interface.tk_vars, 'saving')
    make_spacer(frame, 20)  # Give some space for those dangerous buttons
    make_check_button(frame, interface.tk_vars, 'Auto save')
    make_check_button(frame, interface.tk_vars, 'File append')
    make_check_button(frame, interface.tk_vars, 'File overwrite')
    make_spacer(frame, 20)  # Give some space for those dangerous buttons

    trigger = {'start': False, 'name': entry.get()}
    interface.graph_data['record csv'] = []
    interface.graph_data['auto csv'] = Queue()
    make_thread(build_thread_csv(trigger, interface), interface, 'Csv manager')


def main():
    root, interface = build_interface()
    interface.start_threads()
    root.mainloop()
    interface.stop_threads()


if __name__ == '__main__':
    main()
