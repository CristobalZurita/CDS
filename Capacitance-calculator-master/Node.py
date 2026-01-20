#Node class

class Node:
    def __init__(self, type=None, cargo=None, next=None):
        self.cargo = cargo
        self.next = next
        self.type = type

    def __str__(self):
        return str(self.cargo)

    def set_value(self, t, c):
        self.type = t
        self.cargo = c

    def append_a_node(self, new_node):
        current_node = self
        while current_node.next is not None:
            current_node = current_node.next
        current_node.next = new_node

    # FAIL :(
    def clearList(self):
        current_node = self
        while current_node is not None:
            print(str(current_node))
            place_node = current_node.next
            del current_node
            current_node = place_node