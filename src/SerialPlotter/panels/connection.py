from typing import List

from serial.tools.list_ports import comports

from .. import mvc
from ..manager import TaskInterface


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        # Header label available devices
        # Label which will list selectable devices
        # Controller logic will update this text
        self.create_label_header('Available devices:')
        self.create_label('Ports', 'Please press refresh').configure(height=4)
        self.create_button('Refresh', 'Refresh')

        # Header label device status
        # Label which will list the device status
        # Controller logic will update this text
        self.create_label_header('Device status:')
        self.create_label('Success', 'Please select a device')

        # Header label select device
        # Combobox which list available devices to connect
        # Controller logic will update the list of devices
        self.create_label_header('Select device:')
        self.create_combobox('Device', 'None')

        # Buttons which are controlling the connection
        self.create_button('Connect', 'Connect')
        self.create_button('Disconnect', 'Disconnect')
        self.create_button('Reconnect', 'Reconnect')


class Model:
    def __init__(self):
        pass


class Controller(mvc.Controller):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)
        self.view.bind_button('Connect', self.command_connect)
        self.view.bind_button('Disconnect', self.command_disconnect)
        self.view.bind_button('Reconnect', self.command_reconnect)
        self.view.bind_button('Refresh', self.command_refresh)

        self.queue_in = interface.serial_interface.create_queue('status')
        self.queue_out = interface.serial_interface.create_queue('command')

    def on_close(self):
        pass

    def update_model(self):
        pass

    def update_view(self):
        pass

    def update_display_status(self):
        status = ''
        while not self.queue_in.empty():
            status += self.queue_in.get() + '\n'
        if status == '':
            self.view.after(500, self.update_display_status)
            return
        self.view.update_label('Success', status)

    def command_connect(self):
        # Read the selected device name from the combobox
        device_name = self.view.combo_boxes['Device'].get()
        # Attempt connecting to the selected device
        self.queue_out.put('connect ' + device_name)
        self.view.after(500, self.update_display_status)
        # Update the connection status label
        self.view.update_label('Success', 'Connecting to device...')

    def command_disconnect(self):
        # Attempt disconnecting from the current device
        self.queue_out.put('disconnect')
        self.view.after(500, self.update_display_status)
        # Update the connection status label
        self.view.update_label('Success', 'Disconnecting from device...')

    def command_reconnect(self):
        # Attempt disconnecting and reconnecting to the current device
        self.queue_out.put('reconnect')
        self.view.after(500, self.update_display_status)
        # Update the connection status label
        self.view.update_label('Success', 'Reconnecting to device...')

    def command_refresh(self):
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
