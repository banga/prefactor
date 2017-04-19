import util


class NodeVisitor(object):
    def visit(self, node):
        method_name = "visit_" + util.type_name(node)
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        else:
            self.generic_visit(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)
