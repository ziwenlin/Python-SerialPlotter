import tkinter as tk
from queue import Queue

from serial.tools.list_ports import comports

from filehandler import csv_save_append, csv_save_create
from interfacebuilder import make_base_frame, make_spaced_label, make_button, make_spacer, \
    make_updatable_label, InterfaceVariables, make_combobox, make_graph, make_thread, make_check_button, \
    make_named_spinbox, make_labeled_entry
from threadbuilder import build_thread_interface, build_thread_graph, build_thread_csv


def build_interface():
    top = tk.Tk()
    interface = InterfaceVariables()
    panel_port_selector(top, interface)
    panel_save_control(top, interface)
    panel_graph_control(top, interface)
    panel_graph_filter(top, interface)
    panel_graph_view(top, interface)
    interface.import_settings()

    return top, interface


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
    make_spaced_label(frame, 'Graph filters:')
    # graph_filter = tk.Frame(frame)
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
        # name = trigger['name']
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
        trigger['name'] = entry.get()
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


def __main__():
    root, interface = build_interface()
    interface.start_threads()
    root.mainloop()
    interface.stop_threads()


if __name__ == '__main__':
    __main__()
