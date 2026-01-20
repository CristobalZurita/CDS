from __future__ import division


def calculate(node):
    ecap = -1
    if type(node.cargo) is not node:
        print(node)
        ecap = node.cargo
        node = node.next
    while node:
        if type(node.cargo) is int:
            print(node)
            ecap = add(node, ecap)
            node = node.next
        else:
            if node.type is 'P':
                ecap = ecap + calculate(node.cargo)
            else:
                ecap = 1 / (1 / ecap + 1 / calculate(node.cargo))
            node = node.next
    return ecap


def add(node, ecap):
    if node.type is 'P':
        return ecap + node.cargo
    else:
        return 1 / (1 / ecap + 1 / node.cargo)

