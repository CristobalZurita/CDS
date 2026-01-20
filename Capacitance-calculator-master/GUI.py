from Capacitor import *
from Node import *
from ttk import *
from CircuitBox import *


class GUI:
    def __init__(self, root):
        self.seriesBool = True

        root.wm_title("Calculate This!")
        self.addSeries = Button(root, text="ADD Series", width=10)
        self.calculatefun = Button(root, text="Calc", width=10)
        self.changeB = Button(root, text="Change", width=10)
        self.clearB = Button(root, text="CLEAR", width=10)
        self.moveB = Button(root, text="MOVE", width=10)
        self.branchB = Button(root, text="Series on Branch", state=DISABLED)
        self.num_value = Entry(root, width=30)
        # pack
        self.addSeries.grid(row=0, column=0)
        self.calculatefun.grid(row=1, column=0)
        self.changeB.grid(row=2, column=0)
        self.clearB.grid(row=3, column=0)
        self.moveB.grid(row=2, column=1, sticky=W)
        self.branchB.grid(row=2, column=1, sticky=E)
        self.num_value.grid(row=0, column=1)

        # Bind
        self.calculatefun.bind("<Button-1>", lambda event: printCap(event, stackNode[0]))
        self.addSeries.bind("<Button-1>", lambda event: addB(event, stackNode[len(stackNode) - 1], ))
        self.changeB.bind("<Button-1>", self.change)
        self.clearB.bind("<Button-1>", lambda event: clearNode(event, stackNode[0]))
        self.moveB.bind("<Button-1>", self.move_to_node)

        self.circuit_box = CircuitBox(root)

    # def addText(self, text):
    #     self.T.insert(END, text)
    #     self.T.see(END)

    def change(self, event):
        print("Change")
        # Changing from Series to Parallel
        if self.seriesBool:
            stackNode.append(Node())
            stackNode[0].append_a_node(Node('S', stackNode[1]))
            self.addSeries.configure(text="ADD Parallel")
            self.addSeries.bind("<Button-1>",
                                lambda event: addP(event, stackNode[len(stackNode) - 1]))  # , int(self.num_value.get())
        # Changing from  Parallel to Series
        else:
            self.addSeries.configure(text="ADD Series")
            self.addSeries.bind("<Button-1>", lambda event: addB(event, stackNode[len(stackNode) - 1]))
        self.seriesBool = not self.seriesBool

    def move_to_node(self, event):
        print("move")
        if len(stackNode) > 1:
            del stackNode[len(stackNode) - 1]
            if self.seriesBool:
                self.addSeries.configure(text="ADD Parallel")
                self.addSeries.bind("<Button-1>", lambda event: addP(event, stackNode[len(stackNode) - 1]))
                # Changing from  Parallel to Series
            else:
                self.addSeries.configure(text="ADD Series")
                self.addSeries.bind("<Button-1>", lambda event: addB(event, stackNode[len(stackNode) - 1]))
            self.seriesBool = not self.seriesBool

    def get_num(self):
        value = self.num_value.get()
        if value is not None:
            return int(value)
        else:
            return 0

    def clear_entry(self):
        self.num_value.delete(0, END)


def clearNode(event, nodeVar):
    nodeVar = Node()
    stackNode[0] = nodeVar
    print ("CLEAR called")


def printCap(event, nodeVar):
    print ("Calculate Clicked")
    print("final ecap is " + str(calculate(nodeVar)))


def addP(event, node_var):
    if b.get_num() is None:
        print ("NOne")
    else:
        if node_var.cargo is None:
            node_var.set_value('P', b.get_num())
        else:
            node_var.append_a_node(Node('P', b.get_num()))
        print (str(b.get_num()))
        b.clear_entry()
        return node_var


def addB(event, node_var):
    if b.get_num() is None:
        print ("NOne")
    else:
        b.circuit_box.addSeries()
        print("Add series Called")
        if node_var.cargo is None:
            node_var.set_value('S', b.get_num())
        else:
            node_var.append_a_node(Node('S', b.get_num()))
        print (str(b.get_num()))
        b.clear_entry()
        return node_var


# MAIN

# Acts as a stack
stackNode = [Node()]

root = Tk()
root.style = Style()
root.style.theme_use("clam")
b = GUI(root)
root.mainloop()
