import tkinter as tk
import tkinter.ttk as ttk
from queue import Queue
from typing import Dict, List

from serial.tools.list_ports import comports

from .filehandler import csv_save_append, csv_save_create
from .interfacebuilder import make_base_frame, make_spaced_label, make_button, make_spacer, \
    make_updatable_label, InterfaceVariables, make_combobox, make_graph, make_thread, make_check_button, \
    make_named_spinbox, make_labeled_entry
from .threadbuilder import build_thread_interface, build_thread_graph, build_thread_csv


class ApplicationView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.notebook_tabs: Dict[str, tk.Frame] = {}

        # Create a notebook as main menu
        self.notebook = notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, fill='both', expand=True, anchor='w')

        # Create the tab frames
        self.create_notebook_tab('Connection')
        self.create_notebook_tab('Recorder')
        self.create_notebook_tab('Graph display')
        self.create_notebook_tab('Graph settings')

    def create_notebook_tab(self, name: str):
        frame = tk.Frame(self.notebook)
        frame.configure(pady=10, padx=10)
        frame.pack(fill='both', expand=True, side='left')
        self.notebook.add(frame, text=name)
        self.notebook_tabs[name] = frame
        return frame


class ApplicationController:
    def __init__(self, master, interface):
        self.view = ApplicationView(master)
        self.view.pack(fill='both', expand=True)

        # Gather the frames of the notebook tabs
        tab_connection = self.view.notebook_tabs['Connection']
        tab_recorder = self.view.notebook_tabs['Recorder']
        tab_graph_display = self.view.notebook_tabs['Graph display']
        tab_graph_settings = self.view.notebook_tabs['Graph settings']

        # Create sub controllers and link it to the notebook tabs
        self.device_controller = DevicePanelController(tab_connection, interface)
        self.recorder_controller = RecorderPanelController(tab_recorder, interface)

        # Fill the tabs with the content
        panel_port_selector(tab_connection, interface)
        panel_save_control(tab_recorder, interface)
        panel_graph_control(tab_graph_settings, interface)
        panel_graph_filter(tab_graph_display, interface)
        panel_graph_view(tab_graph_display, interface)

    def todo(self):
        pass


class MVCView:
    def __init__(self):
        self.labels: Dict[str, tk.Label] = {}
        self.buttons: Dict[str, tk.Button] = {}
        self.entries: Dict[str, tk.Entry] = {}

    def update_label(self, name: str, text: str):
        """
        Updates the text inside the desired label.

        :param name: Name of the label
        :param text: Desired text
        """
        label = self.labels.get(name)
        size = text.count('\n') + 1
        label.config(height=size, text=text)

    def bind_button(self, name: str, command: ()):
        """
        Binds the command to the desired button.

        :param name: Name of the button
        :param command: Desired function
        """
        button = self.buttons.get(name)
        button.configure(command=command)


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
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13'
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


class DevicePanelView(tk.Frame, MVCView):
    def __init__(self, master):
        super().__init__(master)
        MVCView.__init__(self)
        self.cboxes: Dict[str, ttk.Combobox] = {}

        # Header label available devices
        label_header_devices = tk.Label(self, text='Available devices:')
        label_header_devices.configure(anchor='nw', padx=5, height=1)
        label_header_devices.pack(fill='both', pady=(10, 2))

        # Label which will list selectable devices
        # Controller logic will update this text
        label_list_devices = tk.Label(self, text='Please press refresh')
        label_list_devices.configure(anchor='nw', padx=10, height=4, justify='left')
        label_list_devices.pack(fill='both')
        self.labels['Ports'] = label_list_devices

        # Header label device status
        label_header_device_status = tk.Label(self, text='Device status:')
        label_header_device_status.configure(anchor='nw', padx=5, height=1)
        label_header_device_status.pack(fill='both', pady=(20, 0))

        # Label which will list the device status
        # Controller logic will update this text
        label_info_device_status = tk.Label(self, text='Please select a device')
        label_info_device_status.configure(anchor='nw', padx=10, height=1)
        label_info_device_status.pack(fill='both')
        self.labels['Success'] = label_info_device_status

        # Header label select device
        label_header_combobox = tk.Label(self, text=f'Select device:')
        label_header_combobox.configure(anchor='nw', padx=5, height=1)
        label_header_combobox.pack(fill='both', pady=(20, 5))

        # Combobox which list available devices to connect
        # Controller logic will update the list of devices
        combobox = ttk.Combobox(self)
        combobox.pack(fill='both', pady=(0, 12))
        combobox.set('None')
        self.combobox = combobox

        # Buttons with the display labels
        button_names = ['Refresh', 'Connect', 'Disconnect', 'Reconnect', 'Send']
        for name in button_names:
            button = tk.Button(self, text=name)
            button.configure(height=2, anchor='w', padx=8)
            self.buttons[name] = button

        # Placing devices controller panel buttons in desired order
        self.buttons['Refresh'].pack(fill='both')
        self.buttons['Connect'].pack(fill='both')
        self.buttons['Disconnect'].pack(fill='both')
        self.buttons['Reconnect'].pack(fill='both')

        # Header label send command
        label_header_send_command = tk.Label(self, text='Send command to device:')
        label_header_send_command.configure(anchor='nw', padx=5, height=1)
        label_header_send_command.pack(fill='both', pady=(20, 2))

        # Entry for send command
        entry_send_command = tk.Entry(self)
        entry_send_command.pack(fill='both', pady=(0, 12))
        # Placing send button after the entry
        self.buttons['Send'].pack(fill='both')
        self.entry = entry_send_command


class DevicePanelModel:
    def __init__(self):
        pass


class DevicePanelController:
    def __init__(self, master, interface):
        self.interface = interface
        self.view = DevicePanelView(master)
        self.view.pack(fill='both', side='left', expand=True)
        self.view.bind_button('Connect', self.connect_command)
        self.view.bind_button('Disconnect', self.disconnect_command)
        self.view.bind_button('Reconnect', self.reconnect_command)
        self.view.bind_button('Refresh', self.refresh_command)
        self.view.bind_button('Send', self.send_command)

    def connect_command(self):
        # Read the selected device name from the combobox
        device_name = self.view.combobox.get()

        # Get the serial controller from the ???
        # Attempt connecting to the selected device
        controller = self.interface.arduino
        success = controller.connect(device_name)

        # Translate success into a status message
        if success is True:
            status = 'Succesfully connected'
        elif success is False:
            status = 'Already connected'
        else:
            status = 'Could not connect'

        # Update the connection status label
        self.view.update_label('Success', status)

    def disconnect_command(self):
        # Get the serial controller from the ???
        # Attempt disconnecting from the current device
        controller = self.interface.arduino
        success = controller.disconnect()

        # Translate success into a status message
        if success is True:
            message = 'Disconnected'
        elif success is False:
            message = 'Not connected'
        else:  # This line should/will never happen
            message = 'Fatal error'

        # Update the connection status label
        self.view.update_label('Success', message)

    def reconnect_command(self):
        # Get the serial controller from the ???
        # Get the currently connected device name
        controller = self.interface.arduino
        device_name = controller.serial.name

        # Attempt disconnecting and reconnecting to the current device
        success_disconnect = controller.disconnect()
        success_connect = controller.connect(device_name)

        # Translate success into a status message
        if success_disconnect and success_connect is True:
            message = 'Reconnected'
        elif success_disconnect and success_connect is False:
            # To be done: What will happen here?
            message = 'Connected? To do'
        else:
            # To be done: What will happen here?
            message = 'Not connected? To do'

        # Update the connection status label
        self.view.update_label('Success', message)

    def refresh_command(self):
        # Gather the ports and extract the device names into a new list
        device_names = [port.device for port in comports()]

        # Enumerate through devices and split them along the label rows
        # The data get filled as follows: rows first then next column
        label_size = self.view.labels.get('Ports')['height']
        label_data: List[List[str]] = [[] for _ in range(label_size)]
        for index, name in enumerate(device_names):
            index_row = index % label_size
            label_data[index_row].append(name)

        # Iterate through the label data and creates the displayed text
        label_text = ''
        for names in label_data:
            for name in names:
                label_text += name + '\t'
            label_text += '\n'
        # Removing last line as that one is not necessary
        label_text = label_text[:-1]

        # When there are no devices connected
        # Creates a warning message to the user
        if len(device_names) == 0:
            label_text += 'No devices available or connected!\n'
            label_text += 'Please try again...\n\n'
            device_names += ['None']

        # Update the text inside the label and the data inside the combobox
        self.view.update_label('Ports', label_text)
        self.view.combobox['values'] = device_names

    def send_command(self):
        data = self.view.entry.get()
        self.view.entry.delete(0, tk.END)
        self.interface.arduino.queue_out.put(data)


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


class RecorderPanelView(tk.Frame, MVCView):
    def __init__(self, master):
        super().__init__(master)
        MVCView.__init__(self)

        self.check_buttons: Dict[str, tk.Checkbutton] = {}

        # Header label file name
        label_header_file_name = tk.Label(self, text='File name:')
        label_header_file_name.configure(anchor='nw', padx=5, height=1)
        label_header_file_name.pack(fill='both', pady=(10, 2))

        # Entry for file name
        entry_file_name = tk.Entry(self)
        entry_file_name.pack(fill='both', pady=(0, 12))
        self.entry = entry_file_name

        # Header label recorder controls
        label_header_recording = tk.Label(self, text='Recorder controls:')
        label_header_recording.configure(anchor='sw', padx=5, height=1)
        label_header_recording.pack(fill='both', pady=(20, 2))

        # Buttons with the display labels
        button_names = ['Start', 'Pause', 'Save']
        for name in button_names:
            button = tk.Button(self, text=name)
            button.configure(height=2, anchor='w', padx=8)
            self.buttons[name] = button

        # Placing recorder controller panel buttons in desired order
        self.buttons['Start'].pack(fill='both')
        self.buttons['Pause'].pack(fill='both')
        self.buttons['Save'].pack(fill='both')

        # Header label recorder status
        label_header_recorder_status = tk.Label(self, text='Recorder status:')
        label_header_recorder_status.configure(anchor='nw', padx=5, height=1)
        label_header_recorder_status.pack(fill='both', pady=(20, 0))

        # Label which will list the recorder status
        # Controller logic will update this text
        label_info_device_status = tk.Label(self, text='Standby')
        label_info_device_status.configure(anchor='nw', padx=10, height=1)
        label_info_device_status.pack(fill='both')
        self.labels['Status'] = label_info_device_status

        # Header label recorder settings
        label_header_recorder_settings = tk.Label(self, text='Recorder settings:')
        label_header_recorder_settings.configure(anchor='nw', padx=5, height=1)
        label_header_recorder_settings.pack(fill='both', pady=(20, 0))

        option_names = ['Auto save', 'File append', 'File overwrite']
        for name in option_names:
            check_button = tk.Checkbutton(self, text=name)
            self.check_buttons[name] = check_button

        self.check_buttons['Auto save'].pack(anchor='w')
        self.check_buttons['File append'].pack(anchor='w')
        self.check_buttons['File overwrite'].pack(anchor='w')

        # IDK what these would do, but it should not be in view
        # trigger = {'start': False, 'name': entry.get()}
        # interface.graph_data['record csv'] = []
        # interface.graph_data['auto csv'] = Queue()
        # make_thread(build_thread_csv(trigger, interface), interface, 'Csv manager')


class RecorderPanelController:
    def __init__(self, master, interface):
        self.interface = interface
        self.view = RecorderPanelView(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)


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
        else:  # Fatal error
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
    root = tk.Tk()
    # To be done: This should be model
    interface = InterfaceVariables()

    controller = ApplicationController(root, interface)
    controller.todo()

    # To be done: Change interface to controller
    interface.import_settings()
    interface.start_threads()
    root.mainloop()
    interface.stop_threads()
    interface.export_settings()


if __name__ == '__main__':
    __main__()
