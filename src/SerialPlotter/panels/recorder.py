from .. import mvc, files
from ..manager import TaskInterface


class View(mvc.ViewBase):
    def __init__(self, master):
        super().__init__(master)
        expand_cnf = {'sticky': 'ns' + 'we'}

        # widget containers
        label = self.labels
        entry = self.entries
        button = self.buttons
        checkbox = self.checkboxes

        # Layout configuration
        self.frame.grid_columnconfigure(0, uniform='a')
        self.frame.grid_columnconfigure(1, uniform='a')
        self.frame.grid_columnconfigure(2, uniform='a')

        # Label frame with status
        frame_status = mvc.LabelFrame(self.frame, 'Recorder status')
        frame_status.grid_configure(row=0, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)
        label['status'] = mvc.Label(frame_status, 'Standby')
        label['status'].pack(fill='both', expand=True, pady=(5, 10))

        # Label frame
        frame_recorder_controls = mvc.LabelFrame(self.frame, 'Recorder controls')
        frame_recorder_controls.grid_configure(row=2, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)
        frame_recorder_controls.grid_columnconfigure(0, uniform='a', weight=1)
        frame_recorder_controls.grid_columnconfigure(1, uniform='a', weight=1)
        frame_recorder_controls.grid_columnconfigure(2, uniform='a', weight=1)

        # Buttons
        button['start'] = mvc.Button(frame_recorder_controls, 'Start')
        button['pause'] = mvc.Button(frame_recorder_controls, 'Pause')
        button['save'] = mvc.Button(frame_recorder_controls, 'Save')
        button['start'].grid_configure(row=0, column=0, cnf=expand_cnf)
        button['pause'].grid_configure(row=0, column=1, cnf=expand_cnf)
        button['save'].grid_configure(row=0, column=2, cnf=expand_cnf)

        # Label frame
        frame_directory = mvc.LabelFrame(self.frame, 'Directory settings')
        frame_directory.grid_configure(row=4, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)
        frame_directory.grid_columnconfigure(0, uniform='a', weight=1)
        frame_directory.grid_columnconfigure(1, uniform='a', weight=1)
        frame_directory.grid_columnconfigure(2, uniform='a', weight=1)

        # Entries with a label
        entry['file_name'] = mvc.LabeledEntry(frame_directory, 'Recording file name')
        entry['directory_data'] = mvc.LabeledEntry(frame_directory, 'Directory for recordings')
        entry['directory_backup'] = mvc.LabeledEntry(frame_directory, 'Directory for backups')
        entry['file_name'].grid_configure(row=0, column=0, columnspan=5, cnf=expand_cnf)
        entry['directory_data'].grid_configure(row=1, column=0, columnspan=5, cnf=expand_cnf)
        entry['directory_backup'].grid_configure(row=2, column=0, columnspan=5, cnf=expand_cnf)

        # Label frame
        frame_directory_controls = mvc.LabelFrame(self.frame, 'Directory controls')
        frame_directory_controls.grid_configure(row=6, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)
        frame_directory_controls.grid_columnconfigure(0, weight=1, uniform='a')
        frame_directory_controls.grid_columnconfigure(1, weight=1, uniform='a')

        # Buttons
        button['directory_data'] = mvc.Button(frame_directory_controls, 'Choose data directory')
        button['directory_backup'] = mvc.Button(frame_directory_controls, 'Choose backup directory')
        button['open_data'] = mvc.Button(frame_directory_controls, 'Open data directory')
        button['open_backup'] = mvc.Button(frame_directory_controls, 'Open backup directory')
        button['directory_data'].grid_configure(row=0, column=0, cnf=expand_cnf)
        button['directory_backup'].grid_configure(row=0, column=1, cnf=expand_cnf)
        button['open_data'].grid_configure(row=1, column=0, cnf=expand_cnf)
        button['open_backup'].grid_configure(row=1, column=1, cnf=expand_cnf)

        # Label frame
        frame_settings = mvc.LabelFrame(self.frame, 'Recorder settings')
        frame_settings.grid_configure(row=8, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)

        # Checkboxes
        checkbox['auto_save'] = mvc.Checkbox(frame_settings, 'Automatically save data when recording')
        checkbox['file_append'] = mvc.Checkbox(frame_settings, 'Append recorder save file data when saving manually')
        checkbox['file_overwrite'] = mvc.Checkbox(frame_settings,
                                                  'Overwrite recorder save file data when saving manually')
        checkbox['auto_save'].pack(anchor='w')
        checkbox['file_append'].pack(anchor='w')
        checkbox['file_overwrite'].pack(anchor='w')

        # Label frame
        frame_settings_controls = mvc.LabelFrame(self.frame)
        frame_settings_controls.grid_configure(row=10, rowspan=2, columnspan=3, column=0, cnf=expand_cnf)
        frame_settings_controls.grid_columnconfigure(0, weight=1, uniform='a')
        frame_settings_controls.grid_columnconfigure(1, weight=1, uniform='a')

        # Buttons
        button['settings_save'] = mvc.Button(frame_settings_controls, 'Save settings')
        button['settings_restore'] = mvc.Button(frame_settings_controls, 'Restore settings')
        button['settings_save'].grid_configure(row=0, column=0, cnf=expand_cnf)
        button['settings_restore'].grid_configure(row=0, column=1, cnf=expand_cnf)


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
        self.view.frame.pack(fill='both', side='left', padx=5, pady=5)
        self.view.frame.after(1000, lambda: self.command_settings())
        self.view.frame.after(2000, lambda: self.update_status('Standby'))

        self.view.buttons['save'].command = self.command_save
        self.view.buttons['start'].command = self.command_start
        self.view.buttons['pause'].command = self.command_pause
        self.view.buttons['directory_data'].command = self.command_directory_data
        self.view.buttons['directory_backup'].command = self.command_directory_backup
        self.view.buttons['open_data'].command = self.command_open_data
        self.view.buttons['open_backup'].command = self.command_open_backup
        self.view.buttons['settings_save'].command = self.command_settings
        self.view.buttons['settings_restore'].command = self.update_view

        self.model.load()
        self.update_view()
        self.queue_command = interface.storage_interface.queue_command
        self.queue_status = interface.storage_interface.queue_status

    def on_close(self):
        self.update_model()
        self.model.save()

    def update_model(self):
        settings = self.model.settings
        settings['file_name'] = self.view.entries['file_name'].get()
        settings['data_dir'] = self.view.entries['directory_data'].get()
        settings['backup_dir'] = self.view.entries['directory_backup'].get()
        settings['auto_save'] = self.view.checkboxes['auto_save'].variable.get()
        settings['file_append'] = self.view.checkboxes['file_append'].variable.get()
        settings['file_overwrite'] = self.view.checkboxes['file_overwrite'].variable.get()

    def update_view(self):
        settings = self.model.settings
        self.view.entries['file_name'].variable.set(settings['file_name'])
        self.view.entries['directory_data'].variable.set(settings['data_dir'])
        self.view.entries['directory_backup'].variable.set(settings['backup_dir'])
        self.view.checkboxes['auto_save'].variable.set(settings['auto_save'])
        self.view.checkboxes['file_append'].variable.set(settings['file_append'])
        self.view.checkboxes['file_overwrite'].variable.set(settings['file_overwrite'])

    def update_status_loop(self):
        status = ''
        while not self.queue_status.empty():
            status += self.queue_status.get() + '\n'
        if status == '':
            self.view.frame.after(500, self.update_status_loop)
            return
        self.update_status(status[:-1])

    def update_status(self, text):
        self.view.labels['status'].set(text)

    def command_directory_data(self):
        path = files.ask_directory()
        if path == '':
            return
        self.view.entries['directory_data'].set(path)

    def command_directory_backup(self):
        path = files.ask_directory()
        if path == '':
            return
        self.view.entries['directory_backup'].set(path)

    def command_open_data(self):
        path = self.view.entries['directory_data'].get()
        files.open_directory(path)

    def command_open_backup(self):
        path = self.view.entries['directory_backup'].get()
        files.open_directory(path)

    def command_settings(self):
        file_name = self.view.entries['file_name'].get()
        self.queue_command.put('file_name ' + file_name.replace(' ', '_'))

        data_dir = self.view.entries['directory_data'].get()
        self.queue_command.put('data_dir ' + data_dir.replace(' ', '%'))

        data_dir = self.view.entries['directory_backup'].get()
        self.queue_command.put('backup_dir ' + data_dir.replace(' ', '%'))

        state_auto_save = self.view.checkboxes['auto_save'].get()
        if state_auto_save is True:
            command = 'auto_save enable'
        else:
            command = 'auto_save disable'
        self.queue_command.put(command)

        self.update_status_loop()
        self.view.frame.winfo_toplevel().event_generate('<<UpdateRecorder>>')

    def command_save(self):
        state_auto_save = self.view.checkboxes['auto_save'].get()
        state_file_append = self.view.checkboxes['file_append'].get()
        state_file_overwrite = self.view.checkboxes['file_overwrite'].get()

        if state_auto_save is True:
            self.update_status('Manually saving is disabled')
            return
        elif state_file_append is True:
            self.update_status_loop()
            self.queue_command.put('recorder save')
            return
        elif state_file_overwrite is True:
            self.update_status_loop()
            self.queue_command.put('recorder overwrite')
            return
        # No settings known is default to nothing
        self.update_status('Standby')
        return

    def command_start(self):
        self.update_status('Waiting for response...')
        self.update_status_loop()
        self.queue_command.put('recorder start')

    def command_pause(self):
        self.update_status('Waiting for response...')
        self.update_status_loop()
        self.queue_command.put('recorder pause')
