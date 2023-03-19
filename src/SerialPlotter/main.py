import tkinter as tk
from queue import Queue
from tkinter import ttk as ttk
from typing import Dict, List

from serial.tools.list_ports import comports

from .filehandler import csv_save_append, csv_save_create
from .interfacebuilder import make_base_frame, make_spaced_label, make_spacer, \
    InterfaceVariables, make_graph, make_thread, make_check_button, \
    make_named_spinbox
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
        frame.configure(pady=5, padx=5)
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
        self.connection_controller = ConnectionPanelController(tab_connection, interface)
        self.recorder_controller = RecorderPanelController(tab_recorder, interface)

        # Fill the tabs with the content
        panel_graph_control(tab_graph_settings, interface)
        panel_graph_filter(tab_graph_display, interface)
        panel_graph_view(tab_graph_display, interface)

    def todo(self):
        pass


class MVCView(tk.Frame):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.text_field: Dict[str, tk.Text] = {}
        self.combo_boxes: Dict[str, ttk.Combobox] = {}
        self.check_buttons: Dict[str, tk.IntVar] = {}
        self.radio_buttons: Dict[str, tk.IntVar] = {}
        self.labels: Dict[str, tk.Label] = {}
        self.buttons: Dict[str, tk.Button] = {}
        self.entries: Dict[str, tk.Entry] = {}

    def update_label(self, name: str, text: str):
        """
        Updates the text inside the desired label.

        :param name: Name of the label
        :param text: Desired text which will be displayed
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

    def create_button(self, name: str, text: str):
        """
        Creates a button with the desired text.

        :param name: Name of the button
        :param text: Text which will be displayed on the button
        """
        button = tk.Button(self, text=text)
        button.configure(height=2, anchor='w', padx=8)
        button.pack(fill='both')
        self.buttons[name] = button
        return button

    def create_label(self, name, text):
        """
        Creates a label with the desired text.

        :param name: Name of the label
        :param text: Desired text which will be displayed
        """
        label = tk.Label(self, text=text)
        label.configure(anchor='nw', padx=10, height=1, justify='left')
        label.pack(fill='both', pady=2)
        self.labels[name] = label
        return label

    def create_label_header(self, text):
        """
        Creates a label with the desired text.

        :param text: Desired text which will be displayed
        """
        label = tk.Label(self, text=text)
        label.configure(anchor='nw', padx=5, height=1)
        label.pack(fill='both', pady=(15, 0))
        return label

    def create_check_button(self, name: str, text: str):
        """
        Creates a checkbutton with the desired text

        :param name: Name of the check button
        :param text: Text which will be displayed on the button
        """
        self.check_buttons[name] = variable = tk.IntVar()
        check_button = tk.Checkbutton(self, text=text, variable=variable)
        check_button.pack(anchor='w')
        return check_button

    def create_entry(self, name: str):
        self.entries[name] = entry = tk.Entry(self)
        entry.pack(fill='both', pady=(5, 20), padx=5)
        return entry

    def create_entry_with_button(self, name: str, text: str):
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=(5, 20), padx=5)

        self.entries[name] = entry = tk.Entry(frame)
        entry.pack(fill='both', side='left', expand=True)

        self.buttons[name] = button = tk.Button(frame, text=text)
        button.configure(anchor='w', padx=8)
        button.pack(fill='both', side='right')

        return frame, entry, button

    def create_combobox(self, name, default_value, values=None):
        if values is None:
            values = []
        self.combo_boxes[name] = combobox = ttk.Combobox(self, values=values)
        combobox.pack(fill='both', padx=5, pady=(5, 20))
        combobox.set(default_value)

    def create_text_field(self, name):
        frame = tk.Frame(self)
        frame.pack(fill='both', expand=True, pady=(5, 20), padx=5)

        self.text_field[name] = text = tk.Text(frame)
        text.pack(fill='both', expand=True, side='left')

        scroll = tk.Scrollbar(frame)
        scroll.pack(fill='both', side='right')

        text.configure(yscrollcommand=scroll.set)
        scroll.configure(command=text.yview)

        return frame, text, scroll

    def create_radio_buttons(self, name, values):
        frame = tk.Frame(self)
        frame.pack(fill='both', pady=(5, 20))

        radio_buttons = []
        self.radio_buttons[name] = variable = tk.IntVar(value=0)

        for index, text in enumerate(values):
            radio_button = tk.Radiobutton(frame, text=text, variable=variable, value=index)
            radio_button.pack(anchor='w')
            radio_buttons.append(radio_button)

        return frame, radio_buttons, variable


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


class DevicePanelView(MVCView):
    def __init__(self, master):
        super().__init__(master)

        # Header label available devices
        self.create_label_header('Available devices:')

        # Label which will list selectable devices
        # Controller logic will update this text
        self.create_label('Ports', 'Please press refresh').configure(height=4)
        self.create_button('Refresh', 'Refresh')

        # Header label device status
        self.create_label_header('Device status:')

        # Label which will list the device status
        # Controller logic will update this text
        self.create_label('Success', 'Please select a device')

        # Header label select device
        self.create_label_header('Select device:')

        # Combobox which list available devices to connect
        # Controller logic will update the list of devices
        self.create_combobox('Device', 'None')

        # Buttons which are controlling the connection
        self.create_button('Connect', 'Connect')
        self.create_button('Disconnect', 'Disconnect')
        self.create_button('Reconnect', 'Reconnect')


class DevicePanelModel:
    def __init__(self):
        pass


class DevicePanelController:
    def __init__(self, master, interface):
        self.interface = interface
        self.view = DevicePanelView(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)
        self.view.bind_button('Connect', self.connect_command)
        self.view.bind_button('Disconnect', self.disconnect_command)
        self.view.bind_button('Reconnect', self.reconnect_command)
        self.view.bind_button('Refresh', self.refresh_command)

    def connect_command(self):
        # Read the selected device name from the combobox
        device_name = self.view.combo_boxes['Device'].get()

        # Get the serial controller from the ???
        # Attempt connecting to the selected device
        controller = self.interface.arduino
        success = controller.connect(device_name)

        # Translate success into a status message
        if success is True:
            status = 'Successfully connected'
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
        self.view.combo_boxes['Device']['values'] = device_names

    def send_command(self):
        entry = self.view.entries['Send']
        data = entry.get()
        entry.delete(0, tk.END)
        self.interface.arduino.queue_out.put(data)


class ConnectionPanelView(MVCView):
    def __init__(self, master):
        super().__init__(master)

        # Header label send command
        # Entry for send command
        # Button which sends the command
        self.create_label_header('Send command to device:')
        self.create_entry_with_button('Out', 'Send')

        # Header label connection settings
        self.create_label_header('Connection data settings:')
        self.create_radio_buttons('Show', [
            'Disable displaying incoming data',
            'Show all', 'Show messages', 'Show data'])

        # Header label incoming data
        self.create_label_header('Incoming data')
        self.create_text_field('In')


class ConnectionPanelController:
    def __init__(self, master, interface):
        self.interface = interface
        self.view = ConnectionPanelView(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)


class RecorderPanelView(MVCView):
    def __init__(self, master):
        super().__init__(master)

        # Header label file name
        self.create_label_header('Save file name:')

        # Entry for file name
        self.create_entry('File name')

        # Button saving recorder data
        self.create_button('Save', 'Save recorded data')

        # Header label recorder controls
        self.create_label_header('Recorder controls:')

        # Buttons with the display labels
        self.create_button('Start', 'Start')
        self.create_button('Pause', 'Pause')

        # Header label recorder status
        self.create_label_header('Recorder status:')

        # Label which will list the recorder status
        # Controller logic will update this text
        self.create_label('Status', 'Standby')

        # Header label recorder settings
        self.create_label_header('Recorder settings:')

        # Check buttons options
        self.create_check_button('Auto save', 'Automatically save incoming data')
        self.create_check_button('File append', 'Append recorder save file data when saving manually')
        self.create_check_button('File overwrite', 'Overwrite recorder save file data when saving manually')


class RecorderPanelController:
    def __init__(self, master, interface):
        self.interface = interface
        self.view = RecorderPanelView(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)

        self.view.bind_button('Save', self.save_command)
        self.view.bind_button('Start', self.start_command)
        self.view.bind_button('Pause', self.pause_command)

        # IDK what these would do, but it should not be in view
        self.trigger = trigger = {'start': False, 'name': self.view.entries['File name'].get()}
        interface.tk_vars['Auto save'] = self.view.check_buttons['Auto save']
        interface.graph_data['record csv'] = []
        interface.graph_data['auto csv'] = Queue()
        make_thread(build_thread_csv(trigger, interface), interface, 'Csv manager')

    def save_command(self):
        record_data = self.interface.graph_data['record csv']
        auto_save_var = self.view.check_buttons['Auto save']
        file_append_var = self.view.check_buttons['File append']
        file_overwrite_var = self.view.check_buttons['File overwrite']
        name = self.view.entries['File name'].get()
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
        self.view.update_label('Status', success)

    def start_command(self):
        self.trigger['start'] = True
        self.trigger['name'] = self.view.entries['File name'].get()
        self.view.update_label('Status', 'Started recording')

    def pause_command(self):
        self.trigger['start'] = False
        self.view.update_label('Status', 'Paused recording')


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
