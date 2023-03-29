import os
import tkinter as tk
import tkinter.filedialog

from .. import mvc
from ..manager import TaskInterface


class View(mvc.ViewOld):
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
        self.create_label_header('Recorder settings:')
        self.create_labeled_entry('File', 'File name:')
        self.create_labeled_entry('Folder', 'Data directory:')
        self.create_labeled_entry('Backup', 'Backup directory:')
        self.create_group('Directory')
        self.create_grouped_button('Directory', 'Folder', 'Choose data directory')
        self.create_grouped_button('Directory', 'Backup', 'Choose backup directory')

        # Recorder settings
        self.create_label_header('Recorder settings:')
        self.create_check_button('Auto save', 'Automatically save data when recording')
        self.create_check_button('File append', 'Append recorder save file data when saving manually')
        self.create_check_button('File overwrite', 'Overwrite recorder save file data when saving manually')

        # Save recorder settings
        self.create_button('Settings', 'Save settings')


class Model(mvc.ModelOld):
    def __init__(self):
        super().__init__('recorder')
        self.settings.update({
            'file_name': '',
            'auto_save': 0,
            'file_append': 0,
            'file_overwrite': 0,
            'data_dir': './data/',
            'backup_dir': './backup/',
        })


class Controller(mvc.ControllerOld):
    def __init__(self, master, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.model.bind(interface)
        self.view = View(master)
        self.view.pack(fill='both', side='left', padx=5, pady=5)
        self.view.after(500, self.command_settings)
        self.view.after(2000, lambda: self.view.update_label('Status', 'Standby'))

        self.view.bind_button('Save', self.command_save)
        self.view.bind_button('Start', self.command_start)
        self.view.bind_button('Pause', self.command_pause)
        self.view.bind_button('Settings', self.command_settings)
        self.view.bind_button('Folder', self.command_directory_data)
        self.view.bind_button('Backup', self.command_directory_backup)

        self.model.load()
        self.update_view()
        self.queue_command = interface.storage_interface.queue_command
        self.queue_status = interface.storage_interface.queue_status

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        settings = self.model.settings
        settings['file_name'] = self.view.entries['File'].get()
        settings['data_dir'] = self.view.entries['Folder'].get()
        settings['backup_dir'] = self.view.entries['Backup'].get()
        settings['auto_save'] = self.view.check_buttons['Auto save'].get()
        settings['file_append'] = self.view.check_buttons['File append'].get()
        settings['file_overwrite'] = self.view.check_buttons['File overwrite'].get()

    def update_view(self):
        settings = self.model.settings
        self.view.entries['File'].delete(0, tk.END)
        self.view.entries['File'].insert(0, settings['file_name'])
        self.view.entries['Folder'].delete(0, tk.END)
        self.view.entries['Folder'].insert(0, settings['data_dir'])
        self.view.entries['Backup'].delete(0, tk.END)
        self.view.entries['Backup'].insert(0, settings['backup_dir'])
        self.view.check_buttons['Auto save'].set(settings['auto_save'])
        self.view.check_buttons['File append'].set(settings['file_append'])
        self.view.check_buttons['File overwrite'].set(settings['file_overwrite'])

    def update_display_status(self):
        status = ''
        while not self.queue_status.empty():
            status += self.queue_status.get() + '\n'
        if status == '':
            self.view.after(500, self.update_display_status)
            return
        self.view.update_label('Status', status[:-1])

    def command_directory_data(self):
        entry = self.view.entries['Folder']
        path = tk.filedialog.askdirectory(initialdir='./')
        if path == '':
            return
        program_path = os.getcwd().replace('\\', '/')
        path = path.replace(program_path, '.') + '/'
        entry.delete(0, tk.END)
        entry.insert(0, path)

    def command_directory_backup(self):
        entry = self.view.entries['Backup']
        path = tk.filedialog.askdirectory(initialdir='./')
        if path == '':
            return
        program_path = os.getcwd().replace('\\', '/')
        path = path.replace(program_path, '.') + '/'
        entry.delete(0, tk.END)
        entry.insert(0, path)

    def command_settings(self):
        file_name = self.view.entries['File'].get()
        self.queue_command.put('file_name ' + file_name.replace(' ', '_'))

        data_dir = self.view.entries['Folder'].get()
        self.queue_command.put('data_dir ' + data_dir.replace(' ', '%'))

        data_dir = self.view.entries['Backup'].get()
        self.queue_command.put('backup_dir ' + data_dir.replace(' ', '%'))

        state_auto_save = self.view.check_buttons['Auto save'].get() == 1
        if state_auto_save is True:
            command = 'auto_save enable'
        else:
            command = 'auto_save disable'
        self.queue_command.put(command)

        self.view.winfo_toplevel().event_generate('<<UpdateRecorder>>')
        self.view.after(500, self.update_display_status)

    def command_save(self):
        state_auto_save = self.view.check_buttons['Auto save'].get() == 1
        state_file_append = self.view.check_buttons['File append'].get() == 1
        state_file_overwrite = self.view.check_buttons['File overwrite'].get() == 1

        if state_auto_save is True:
            self.view.update_label('Status', 'Manually saving is disabled')
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
