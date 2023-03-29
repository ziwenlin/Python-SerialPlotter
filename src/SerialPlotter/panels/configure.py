import tkinter as tk

from .. import mvc
from ..manager import TaskInterface


class Model(mvc.ModelOld):
    def __init__(self):
        super(Model, self).__init__('settings')
        self.settings.update({
            'application_name': 'Serial Plotter',
            'graph_x_min': -10,
            'graph_x_max': 510,
            'graph_y_min': -10,
            'graph_y_max': 110,
            'graph_size': 200,
            'graph_clear': 50,
        })


class View(mvc.ViewOld):
    def __init__(self, master):
        super().__init__(master)

        self.create_label_header('Application settings:')
        self.create_labeled_entry('Window', 'Window name:')

        self.create_label_header('Graph view settings:')
        self.create_ranged_slider('X', 'X-axis range:', [-1000, 10000, 1])
        self.create_ranged_slider('Y', 'Y-axis range:', [-1000, 10000, 1])

        self.create_spinbox('Size', 'Graph size', [1, 10000, 100])
        self.create_spinbox('Clear', 'Clear size', [1, 10000, 100])

        self.create_group('Buttons')
        self.create_grouped_button('Buttons', 'Save', 'Save settings')
        self.create_grouped_button('Buttons', 'Load', 'Restore settings')


class Controller(mvc.ControllerOld):
    def __init__(self, master: tk.Frame, interface: TaskInterface):
        self.interface = interface
        self.model = Model()
        self.model.bind(interface)
        self.view = View(master)
        self.view.pack(fill='both', side='left', padx=5, pady=5)

        self.view.bind_button('Save', lambda: self.command_save())
        self.view.bind_button('Load', lambda: self.command_load())

        self.model.load()
        self.update_view()

    def update_model(self):
        settings = self.model.settings
        settings['application_name'] = self.view.entries['Window'].get()
        self.view.winfo_toplevel().wm_title(settings['application_name'])

        settings['graph_x_min'] = self.view.scales['XMin'].get()
        settings['graph_x_max'] = self.view.scales['XMax'].get()
        settings['graph_y_min'] = self.view.scales['YMin'].get()
        settings['graph_y_max'] = self.view.scales['YMax'].get()

        settings['graph_size'] = self.view.spin_boxes['Size'].get()
        settings['graph_clear'] = self.view.spin_boxes['Clear'].get()

    def update_view(self):
        settings = self.model.settings
        self.view.entries['Window'].delete(0, tk.END)
        self.view.entries['Window'].insert(0, settings['application_name'])
        self.view.winfo_toplevel().wm_title(settings['application_name'])

        self.view.scales['XMin'].set(settings['graph_x_min'])
        self.view.scales['XMax'].set(settings['graph_x_max'])
        self.view.scales['YMin'].set(settings['graph_y_min'])
        self.view.scales['YMax'].set(settings['graph_y_max'])

        self.view.spin_boxes['Size'].set(settings['graph_size'])
        self.view.spin_boxes['Clear'].set(settings['graph_clear'])

    def on_close(self):
        self.update_model()
        self.model.save()

    def command_save(self):
        self.update_model()
        self.model.save()
        self.view.winfo_toplevel().event_generate('<<UpdateSettings>>')

    def command_load(self):
        self.model.load()
        self.update_view()
