import unittest


class TestSetupLibraries(unittest.TestCase):

    @unittest.skip('This test takes 2 seconds to load')
    def test_matplotlib(self):
        try:
            import matplotlib
            success = True
        except:
            success = False
        self.assertTrue(success, 'matplotlib')

    @unittest.skip('This test takes 5 seconds to load')
    def test_matplotlib_plot(self):
        try:
            import matplotlib.pyplot as plt
            plt.plot([1, 2, 3, 4])
            plt.ylabel('some numbers')
            # plt.show()
            success = True
        except:
            success = False
        self.assertTrue(success,'matplotlib_plot')

    def test_tkinter(self):
        try:
            import tkinter
            success = True
        except:
            success = False
        self.assertTrue(success,'tkinter')

    def test_serial(self):
        try:
            import serial.tools.list_ports
            import serial
            success = True
        except:
            success = False
        self.assertTrue(success, 'serial')

    def test_numpy(self):
        try:
            import numpy
            success = True
        except:
            success = False
        self.assertTrue(success, 'numpy')

    def test_threading(self):
        try:
            import threading
            success = True
        except:
            success = False
        self.assertTrue(success, 'threading')

