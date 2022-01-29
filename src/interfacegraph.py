from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class Graph:
    def __init__(self, x_data, y_data=None):
        self.fig = Figure(figsize=(12, 6))
        self.ax = self.fig.add_subplot(111)
        self.is_plotting = False
        self.master = None
        self.canvas = None
        self.toolbar = None
        if y_data is not None:
            self.line, = self.ax.plot(x_data, y_data, linewidth=0.5)
        else:
            self.line, = self.ax.plot(x_data, linewidth=0.5)

    def start(self, master):
        self.is_plotting = True
        self.master = master
        self.canvas = FigureCanvasTkAgg(self.fig, master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update(self, data):
        self.line.set_ydata(data)

    def draw(self):
        try:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        except:
            self.is_plotting = False

    def __del__(self):
        print("Deleting graph")

    def close(self):
        self.master.destroy()
        print("Closing graph")
        del self
