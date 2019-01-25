"""
Adds trailing commas to multi-line dicts
"""
import lib2to3
from lib2to3.pgen2.token import COMMA, NEWLINE
from lib2to3.pytree import Leaf, Node
from util import type_name as type
from visitor import NodeVisitor


class Visitor(NodeVisitor):
    def __init__(self):
        pass

    def visit_dictsetmaker(self, node):
        linenos = set(
            child.get_lineno()
			for child in node.children)

        if len(linenos) <= 1:
            self.generic_visit(node)
            return

        last_child = type(node.children[-1])
       	if last_child == "COMMA" or \
        	last_child == "comp_for":
            self.generic_visit(node)
            return

        comma = Leaf(COMMA, ",")
        node.append_child(comma)
        self.generic_visit(node)