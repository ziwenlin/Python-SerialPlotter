import tkinter as tk

from .. import mvc


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        # Header label send command
        # Entry for send command
        # Button which sends the command
        self.create_label_header('Send command to device:')
        self.create_entry_with_button('Out', 'Send')

        # Header label connection settings
        self.create_label_header('Connection data settings:')

        # Header label incoming data
        self.create_label_header('Incoming data:')
        self.create_radio_buttons('Show', [
            'Disable', 'Show all', 'Show messages', 'Show values'])
        self.create_text_field('In')


class Controller(mvc.Controller):
    def __init__(self, master, interface):
        self.interface = interface
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)
        self.view.bind_button('Out', self.send_command)

    def on_close(self):
        pass

    def update_model(self):
        pass

    def update_view(self):
        pass

    def send_command(self):
        entry = self.view.entries['Out']
        data = entry.get()
        entry.delete(0, tk.END)
        self.interface.arduino.queue_out.put(data)
