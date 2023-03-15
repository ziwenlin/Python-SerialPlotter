from typing import List

from serial.tools.list_ports import comports

from .. import mvc
from ..manager import TaskInterface


class View(mvc.ViewOld):
    def __init__(self, master):
        super().__init__(master)

        # Header label available devices
        # Label which will list selectable devices
        # Controller logic will update this text
        self.create_label_header('Available devices:')
        self.create_label('Ports', 'Please press refresh').configure(height=4)
        self.create_button('Refresh', 'Refresh')

        # Header label select device
        # Combobox which list available devices to connect
        # Controller logic will update the list of devices
        self.create_label_header('Select device:')
        self.create_check_button('Remember', 'Remember')
        self.create_combobox('Device', 'None')

        # Header label device status
        # Label which will list the device status
        # Controller logic will update this text
        self.create_label_header('Device status:')
        self.create_label('Status', 'Please select a device').configure(width=30)

        # Buttons which are controlling the connection
        self.create_group('Controls')
        self.create_grouped_button('Controls', 'Connect', 'Connect')
        self.create_grouped_button('Controls', 'Disconnect', 'Disconnect')
        self.create_grouped_button('Controls', 'Reconnect', 'Reconnect')


class Model(mvc.ModelOld):
    def __init__(self):
        super(Model, self).__init__('connection')
        self.settings.update({
            'device': '',
            'keep': 0,
        })


class Controller(mvc.ControllerOld):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.model.bind(interface)
        self.view = View(master)
        self.view.pack(fill='both', side='left', padx=5, pady=5)
        self.view.bind_button('Connect', self.command_connect)
        self.view.bind_button('Disconnect', self.command_disconnect)
        self.view.bind_button('Reconnect', self.command_reconnect)
        self.view.bind_button('Refresh', self.command_refresh)

        self.model.load()
        self.update_view()
        self.queue_in = interface.serial_interface.create_queue('status')
        self.queue_out = interface.serial_interface.create_queue('command')

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        settings = self.model.settings
        settings['device'] = ''
        settings['keep'] = self.view.check_buttons['Remember'].get()
        if settings['keep'] == 1:
            settings['device'] = self.view.combo_boxes['Device'].get()

    def update_view(self):
        settings = self.model.settings
        if settings['keep'] == 1:
            self.view.combo_boxes['Device'].delete(0, 'end')
            self.view.combo_boxes['Device'].insert(0, settings['device'])
        self.view.check_buttons['Remember'].set(settings['keep'])

    def update_display_status(self):
        status = ''
        while not self.queue_in.empty():
            status += self.queue_in.get() + ' '
        if status == '':
            self.view.after(500, self.update_display_status)
            return
        self.view.update_label('Status', status)

    def command_connect(self):
        # Read the selected device name from the combobox
        device_name = self.view.combo_boxes['Device'].get()
        # Attempt connecting to the selected device
        self.queue_out.put('connect ' + device_name)
        self.view.after(500, self.update_display_status)
        # Update the connection status label
        self.view.update_label('Status', 'Connecting to device...')

    def command_disconnect(self):
        # Attempt disconnecting from the current device
        self.queue_out.put('disconnect')
        self.view.after(500, self.update_display_status)
        # Update the connection status label
        self.view.update_label('Status', 'Disconnecting from device...')

    def command_reconnect(self):
        # Attempt disconnecting and reconnecting to the current device
        self.queue_out.put('reconnect')
        self.view.after(500, self.update_display_status)
        # Update the connection status label
        self.view.update_label('Status', 'Reconnecting to device...')

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
