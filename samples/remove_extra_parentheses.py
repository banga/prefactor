"""
Removes extra parentheses around await statements
"""
from util import type_name as type
from visitor import NodeVisitor


def is_multiline(power_node):
    if (power_node.prev_sibling.get_lineno() !=
        power_node.get_lineno()):
        return True

    nodes = power_node.children[2:]

    current_line = power_node.get_lineno()
    next_line = current_line
    for node in nodes:
        if type(node) != "trailer":
            print("Unknown node", node)
        elif node.get_lineno() != current_line:
            return True

    return False


class Visitor(NodeVisitor):
    def __init__(self):
        pass

    def visit_power(self, node):
        skip = False

        # not in an await statement
        if type(node.children[0]) != "AWAIT":
            skip = True
        # no parentheses
        elif (not node.prev_sibling or
            not node.next_sibling or
            type(node.prev_sibling) != "LPAR" or
            type(node.next_sibling) != "RPAR"):
            skip = True
        # we are in an attribute access
        elif type(node.parent) == "trailer":
            skip = True
        # parentheses for attribute access
        elif (node.parent.next_sibling and
            type(node.parent.next_sibling) == "trailer"):
            skip = True
        # parentheses around multiline await
        elif is_multiline(node):
            skip = True

        if skip:
            self.generic_visit(node)
            return

        print("Removing parentheses around:", node)

        node.prefix = node.prev_sibling.prefix + node.prefix
        node.prev_sibling.remove()
        node.next_sibling.remove()
