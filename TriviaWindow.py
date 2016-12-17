from PySide.QtGui import *
from PySide.QtCore import *
from TriviaWidget import TriviaWidget

class TriviaWindow(QMainWindow):
    def __init__(self):
        super(TriviaWindow, self).__init__()
        widget = TriviaWidget()
        self.setCentralWidget(widget)
        self.setWindowTitle("Lake Orion Swim and Dive Trivia")
        self.showMaximized()
