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


class ViewNew(mvc.ViewBase):
    def __init__(self, master):
        super().__init__(master)
        expand_cnf = {'sticky': 'ns' + 'we'}
        frame_cnf = {'padx': 5, 'pady': 5}

        # widget containers
        label = self.labels
        entry = self.entries
        button = self.buttons
        spinbox = self.spinboxes

        # Layout configuration
        self.frame.grid_columnconfigure(0, uniform='a')
        self.frame.grid_columnconfigure(1, uniform='a')
        self.frame.grid_columnconfigure(2, uniform='a')
        self.frame.grid_rowconfigure(99, weight=1)

        # Frame for application settings
        frame_application = tk.LabelFrame(self.frame, text='Application settings', cnf=frame_cnf)
        frame_application.grid_configure(row=0, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)
        frame_application.columnconfigure(0, uniform='a', weight=1)
        frame_application.columnconfigure(1, uniform='a', weight=1)
        frame_application.columnconfigure(2, uniform='a', weight=1)

        # Contents application settings frame
        label['app_title'] = mvc.Label(frame_application, 'Application name')
        label['app_title'].grid_configure(row=1, column=0)
        entry['app_title'] = mvc.Entry(frame_application)
        entry['app_title'].grid_configure(row=1, column=1, columnspan=2)
        entry['app_title'].grid_configure(cnf=expand_cnf)

        # Frame for graph view settings
        frame_graph = tk.LabelFrame(self.frame, text='Graph view settings', cnf=frame_cnf)
        frame_graph.grid_configure(row=2, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)
        frame_graph.columnconfigure(0, uniform='a', weight=1)
        frame_graph.columnconfigure(1, uniform='a', weight=1)
        frame_graph.columnconfigure(2, uniform='a', weight=1)

        # Contents graph view settings
        label['graph_x_axis'] = mvc.Label(frame_graph, 'Range x-axis')
        label['graph_y_axis'] = mvc.Label(frame_graph, 'Range y-axis')
        label['graph_min'] = mvc.Label(frame_graph, 'Minimum')
        label['graph_max'] = mvc.Label(frame_graph, 'Maximum')
        label['graph_min'].grid_configure(row=0, column=1)
        label['graph_max'].grid_configure(row=0, column=2)
        label['graph_x_axis'].grid_configure(row=1)
        label['graph_y_axis'].grid_configure(row=2)

        # Contents graph view settings
        spinbox['graph_x_min'] = mvc.Spinbox(frame_graph, (-1000, 0, 10))
        spinbox['graph_x_max'] = mvc.Spinbox(frame_graph, (10, 10000, 10))
        spinbox['graph_y_min'] = mvc.Spinbox(frame_graph, (-1000, 0, 10))
        spinbox['graph_y_max'] = mvc.Spinbox(frame_graph, (10, 10000, 10))
        spinbox['graph_x_min'].grid_configure(row=1, column=1, cnf=expand_cnf)
        spinbox['graph_x_max'].grid_configure(row=1, column=2, cnf=expand_cnf)
        spinbox['graph_y_min'].grid_configure(row=2, column=1, cnf=expand_cnf)
        spinbox['graph_y_max'].grid_configure(row=2, column=2, cnf=expand_cnf)

        # Frame for graph data settings
        frame_data = tk.LabelFrame(self.frame, text='Graph data settings', cnf=frame_cnf)
        frame_data.grid_configure(row=4, column=0, rowspan=2, columnspan=3, cnf=expand_cnf)
        frame_data.columnconfigure(0, uniform='a', weight=1)
        frame_data.columnconfigure(1, uniform='a', weight=1)
        frame_data.columnconfigure(2, uniform='a', weight=1)

        # Contents of graph data settings frame
        label['graph_data_size'] = mvc.Label(frame_data, 'Total of points')
        label['graph_clear_size'] = mvc.Label(frame_data, 'Clear amount')
        label['graph_data_size'].grid_configure(row=3)
        label['graph_clear_size'].grid_configure(row=4)

        # Contents of graph data settings frame
        spinbox['graph_data_size'] = mvc.Spinbox(frame_data, (10, 10000, 10))
        spinbox['graph_clear_size'] = mvc.Spinbox(frame_data, (10, 10000, 10))
        spinbox['graph_data_size'].grid_configure(row=3, column=1, cnf=expand_cnf)
        spinbox['graph_clear_size'].grid_configure(row=4, column=1, cnf=expand_cnf)

        # Buttons for saving settings inside this view
        button['save'] = mvc.Button(self.frame, 'Save settings')
        button['restore'] = mvc.Button(self.frame, 'Restore settings')
        button['save'].grid_configure(row=100, column=1, cnf=expand_cnf)
        button['restore'].grid_configure(row=100, column=2, cnf=expand_cnf)


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
