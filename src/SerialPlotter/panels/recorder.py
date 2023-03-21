import tkinter as tk

from .. import mvc
from ..manager import TaskInterface


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        # Header label file name
        self.create_label_header('Save file name:')

        # Entry for file name
        self.create_entry_with_button('Save', 'Save')

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


class Model(mvc.Model):
    def __init__(self):
        super().__init__('recorder')
        self.settings.update({
            'file_name': '',
            'auto_save': 0,
            'file_append': 0,
            'file_overwrite': 0,
        })


class Controller(mvc.Controller):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.model.bind(interface)
        self.view = View(master)
        self.view.pack(fill='both', side='left', expand=True, padx=5, pady=5)

        self.view.bind_button('Save', self.command_save)
        self.view.bind_button('Start', self.command_start)
        self.view.bind_button('Pause', self.command_pause)

        self.model.load()
        self.update_view()
        self.queue_command = interface.storage_interface.queue_command
        self.queue_status = interface.storage_interface.queue_status

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        settings = self.model.settings
        settings['file_name'] = self.view.entries['Save'].get()
        settings['auto_save'] = self.view.check_buttons['Auto save'].get()
        settings['file_append'] = self.view.check_buttons['File append'].get()
        settings['file_overwrite'] = self.view.check_buttons['File overwrite'].get()

    def update_view(self):
        settings = self.model.settings
        self.view.entries['Save'].delete(0, tk.END)
        self.view.entries['Save'].insert(0, settings['file_name'])
        self.view.check_buttons['Auto save'].set(settings['auto_save'])
        self.view.check_buttons['File append'].set(settings['file_append'])
        self.view.check_buttons['File overwrite'].set(settings['file_overwrite'])

    def update_display_status(self):
        status = ''
        while not self.queue_status.empty():
            status += self.queue_status.get() + ' '
        if status == '':
            self.view.after(500, self.update_display_status)
            return
        self.view.update_label('Status', status)

    def command_save(self):
        state_auto_save = self.view.check_buttons['Auto save'].get() == 1
        state_file_append = self.view.check_buttons['File append'].get() == 1
        state_file_overwrite = self.view.check_buttons['File overwrite'].get() == 1

        file_name = self.view.entries['Save'].get()
        self.queue_command.put('file_name ' + file_name.replace(' ', '_'))
        self.view.after(500, self.update_display_status)

        if state_auto_save is True:
            return
        elif state_file_append is True:
            self.queue_command.put('recorder save')
            return
        elif state_file_overwrite is True:
            self.queue_command.put('recorder overwrite')
            return
        # No settings known is default to nothing
        return

    def command_start(self):
        self.queue_command.put('recorder start')
        self.view.after(500, self.update_display_status)
        self.view.update_label('Status', 'Waiting for response...')

    def command_pause(self):
        self.queue_command.put('recorder pause')
        self.view.after(500, self.update_display_status)
        self.view.update_label('Status', 'Waiting for response...')
