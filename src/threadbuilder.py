from queue import Queue

from filehandler import csv_save_append, csv_save_auto, json_save, json_load
from interfacebuilder import InterfaceVariables


# def build_thread_settings(interface: InterfaceVariables):
#     from time import sleep
#
#     def build_json():
#         version = '1.0'
#         tk_vars = {key: value.get() for key, value in interface.tk_vars.items()}
#         tk_data = {'graph': interface.tk_data['graph']}
#         gr_data = {'state': interface.graph_data['state']}
#         json_save({'version': version,
#                    'tk_vars': tk_vars,
#                    'tk_data': tk_data,
#                    'graph_data': gr_data})
#
#     def import_json():
#         settings = interface.settings
#         for key, value in settings.get('tk_vars').items():
#             interface.tk_vars[key].set(value)
#         for key, data in settings.get('tk_data').items():
#             interface.tk_data[key] = data
#         for key, data in settings.get('graph_data').items():
#             interface.graph_data[key] = data


def build_thread_interface(graph, interface: InterfaceVariables):
    from time import sleep
    filter_state = interface.graph_data['state']
    graph_filters = interface.tk_data.get('graph')
    tk_vars = interface.tk_vars

    def interface_manager():
        while interface.running.is_set():
            sleep(0.4)
            if not interface.running.is_set():
                return
            if interface.tk_vars.get('Lock axis').get() == 1:
                try:
                    x_min = float(tk_vars.get('x min').get())
                    x_max = float(tk_vars.get('x max').get())
                    y_min = float(tk_vars.get('y min').get())
                    y_max = float(tk_vars.get('y max').get())
                except ValueError:
                    continue
                if x_min == x_max:
                    x_min -= 1
                if y_min == y_max:
                    y_min -= 1
                graph.plot.set_xlim(x_min, x_max)
                graph.plot.set_ylim(y_min, y_max)
            if not interface.running.is_set():
                return
            if interface.tk_vars.get('Copy axis').get() == 1:
                x_min, x_max = graph.plot.get_xlim()
                y_min, y_max = graph.plot.get_ylim()
                tk_vars.get('x min').set(f'{x_min:.2f}')
                tk_vars.get('x max').set(f'{x_max:.2f}')
                tk_vars.get('y min').set(f'{y_min:.2f}')
                tk_vars.get('y max').set(f'{y_max:.2f}')
            if not interface.running.is_set():
                return
            for i, filter in enumerate(graph_filters):
                state = interface.tk_vars.get(filter).get() == 1
                filter_state.update({i: state})

    return interface_manager


def build_thread_graph(graph, interface: InterfaceVariables):
    from time import sleep
    csv_queue: Queue = interface.graph_data['auto csv']
    filter_state: dict = interface.graph_data['state']
    data: list = []
    queue = interface.arduino.queue_in

    def get_queue_data():
        while not queue.empty():
            serial_data = queue.get()
            for index, value in enumerate(serial_data):
                try:
                    data[index].append(value)
                except IndexError:
                    data.append([value])
            csv_queue.put(serial_data)

    def clean_up_data():
        if len(data) > 1000:
            del data[:500]

    def get_graph_data():
        graph_data: dict = {}
        for index, values in enumerate(data):
            if index in filter_state and filter_state[index] is True:
                graph_data.update({index: values[-200:]})
        return graph_data

    def serial_graph():
        while interface.running.is_set():
            if queue.empty():
                sleep(0.5)
                continue
            get_queue_data()
            clean_up_data()
            graph.update(get_graph_data())
            sleep(0.1)

    return serial_graph


def build_thread_csv(trigger: dict, interface: InterfaceVariables):
    from time import sleep
    auto_queue: Queue = interface.graph_data['auto csv']
    record_data: list = interface.graph_data['record csv']
    auto_data = []
    auto_save_var = interface.tk_vars['Auto save']

    def get_queue_data():
        record: bool = trigger['start']
        while not auto_queue.empty():
            serial_data = auto_queue.get()
            if record:
                record_data.append(serial_data)
            auto_data.append(serial_data)

    def auto_save_data():
        if len(auto_data) < 1000:
            return
        record: bool = trigger['start']
        if record and auto_save_var.get() == 1:
            name = trigger['name']
            csv_save_append(name, record_data)
            record_data.clear()
        csv_save_auto(auto_data)
        auto_data.clear()

    def csv_manager():
        while interface.running.is_set():
            if auto_queue.empty():
                sleep(0.5)
                continue
            get_queue_data()
            auto_save_data()
            sleep(0.1)
        record: bool = trigger['start']
        if record or auto_save_var.get() == 1:
            name = trigger['name']
            csv_save_append(name, record_data)
            record_data.clear()
        csv_save_auto(auto_data)
        auto_data.clear()

    return csv_manager
