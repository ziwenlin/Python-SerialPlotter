from typing import List

from serial.tools.list_ports import comports

from .. import mvc
from ..thread import ThreadInterface


class View(mvc.View):
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


class Model:
    def __init__(self):
        pass


class Controller(mvc.Controller):
    def __init__(self, master, interface: ThreadInterface):
        self.interface = interface
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)
        self.view.bind_button('Connect', self.command_connect)
        self.view.bind_button('Disconnect', self.command_disconnect)
        self.view.bind_button('Reconnect', self.command_reconnect)
        self.view.bind_button('Refresh', self.command_refresh)

    def on_close(self):
        pass

    def update_model(self):
        pass

    def update_view(self):
        pass

    def command_connect(self):
        # Read the selected device name from the combobox
        device_name = self.view.combo_boxes['Device'].get()

        # Get the serial controller from the ???
        # Attempt connecting to the selected device
        controller = self.interface.serial_controller
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

    def command_disconnect(self):
        # Get the serial controller from the ???
        # Attempt disconnecting from the current device
        controller = self.interface.serial_controller
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

    def command_reconnect(self):
        # Get the serial controller from the ???
        # Get the currently connected device name
        controller = self.interface.serial_controller
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
