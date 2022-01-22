import unittest


class TestSetupLibraries(unittest.TestCase):

    def test_matplotlib(self):
        try:
            import matplotlib
        except:
            self.assertFalse(False, 'matplotlib')
        self.assertTrue(True, 'matplotlib')

    def test_matplotlib_plot(self):
        import matplotlib.pyplot as plt
        plt.plot([1, 2, 3, 4])
        plt.ylabel('some numbers')
        plt.show()
        self.assertTrue(True, 'matplotlib_plot')

    def test_tkinter(self):
        try:
            import tkinter
        except:
            self.assertFalse(False, 'tkinter')
        self.assertTrue(True, 'tkinter')
