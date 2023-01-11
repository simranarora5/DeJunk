from PyQt4 import QtGui
from new_window import NewWindow


class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self._new_window = None
        self._button = QtGui.QPushButton('New Window', self)
        self._button.clicked.connect(self.create_new_window)
        self.setCentralWidget(self._button)

    def create_new_window(self):
        self._new_window = NewWindow()
        self._new_window.show()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    gui = Window()
    gui.show()
    app.exec_()