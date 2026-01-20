from Tkinter import *


class CircuitBox:
    def __init__(self, root):
        self.S = Scrollbar(root, orient=HORIZONTAL)
        self.T = Text(root)
        self.T.grid(row=5, sticky=W, columnspan=8)
        self.S.config(command=self.T.xview)
        self.T.config(xscrollcommand=self.S.set)
        self.T.config(wrap=NONE)

        # Counters
        self.counter = 0

    def addSeries(self):
        self.T.insert(END, "--||--")
        self.T.see(END)
        self.counter = self.counter + 6

    def addParallel(self):
        self.T.insert(END, )
