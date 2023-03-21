import tkinter as tk

from .. import mvc
from ..manager import TaskInterface


class View(mvc.View):
    def __init__(self, master):
        super().__init__(master)

        # Recorder status
        # Label which will list the recorder status
        # Controller logic will update this text
        self.create_label_header('Recorder status:')
        self.create_label('Status', 'Standby')

        # Recorder controls
        # Buttons which controls the recorder
        self.create_label_header('Recorder controls:')
        self.create_group('Controls')
        self.create_grouped_button('Controls', 'Start', 'Start')
        self.create_grouped_button('Controls', 'Pause', 'Pause')
        self.create_grouped_button('Controls', 'Save', 'Save')

        # File name entry with button to save
        self.create_label_header('File name:')
        self.create_entry('Save')

        # Recorder settings
        self.create_label_header('Recorder settings:')
        self.create_check_button('Auto save', 'Automatically save data when recording')
        self.create_check_button('File append', 'Append recorder save file data when saving manually')
        self.create_check_button('File overwrite', 'Overwrite recorder save file data when saving manually')

        # Save recorder settings
        self.create_button('Settings', 'Save settings')


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
        self.view.pack(fill='both', side='left', padx=5, pady=5)

        self.view.bind_button('Save', self.command_save)
        self.view.bind_button('Start', self.command_start)
        self.view.bind_button('Pause', self.command_pause)
        self.view.bind_button('Settings', self.command_settings)

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

    def command_settings(self):
        file_name = self.view.entries['Save'].get()
        self.queue_command.put('file_name ' + file_name.replace(' ', '_'))

        state_auto_save = self.view.check_buttons['Auto save'].get() == 1
        if state_auto_save is True:
            self.queue_command.put('auto_save enable')
        else:
            self.queue_command.put('auto_save disable')

        self.view.after(500, self.update_display_status)

    def command_save(self):
        state_auto_save = self.view.check_buttons['Auto save'].get() == 1
        state_file_append = self.view.check_buttons['File append'].get() == 1
        state_file_overwrite = self.view.check_buttons['File overwrite'].get() == 1

        if state_auto_save is True:
            self.view.update_label('Status', 'This feature is disabled')
            return
        elif state_file_append is True:
            self.view.after(500, self.update_display_status)
            self.queue_command.put('recorder save')
            return
        elif state_file_overwrite is True:
            self.view.after(500, self.update_display_status)
            self.queue_command.put('recorder overwrite')
            return
        # No settings known is default to nothing
        self.view.update_label('Status', 'Standby')
        return

    def command_start(self):
        self.queue_command.put('recorder start')
        self.view.after(500, self.update_display_status)
        self.view.update_label('Status', 'Waiting for response...')

    def command_pause(self):
        self.queue_command.put('recorder pause')
        self.view.after(500, self.update_display_status)
        self.view.update_label('Status', 'Waiting for response...')
