"""
Removes unused imports in a file

TODO:
- Add tests
- Handle/ignore conditional global imports
- Handle shadowing variables

"""
from util import type_name
from visitor import NodeVisitor


class Visitor(NodeVisitor):
    def __init__(self):
        self.imports = {}
        self.names = {}
        self.multi_imports = []
        self.in_trailer = 0

    def visit_import_name(self, node):
        name_child = node.children[1]
        type = type_name(name_child)
        if type == "NAME":
            name = name_child.value
        elif type == "dotted_name":
            name = "".join(
                c.value for c in name_child.children)
        elif type == "dotted_as_name":
            name = name_child.children[2].value
        else:
            raise Exception("Unknown type", type)
        self.imports[name] = [node.parent]

    def visit_import_from(self, node):
        name_child = node.children[-1]
        type = type_name(name_child)
        name = ""
        if type == "NAME":
            name = name_child.value
        elif type == "import_as_name":
            name = name_child.children[-1].value
        elif type == "import_as_names":
            self.multi_imports.append(node)
            self.visit_import_as_names(name_child)
        elif type == "RPAR":
            prev_node = name_child.prev_sibling
            assert(type_name(prev_node) == "import_as_names")
            self.multi_imports.append(node)
            self.visit_import_as_names(prev_node)
        else:
            raise Exception("Unknown type", type)
        if name:
            self.imports[name] = [node.parent]

    def visit_import_as_names(self, node):
        for child in node.children:
            type = type_name(child)
            name_child = None
            if type == "COMMA":
                continue
            if type == "import_as_name":
                name_child = child.children[-1]
            elif type == "NAME":
                name_child = child
            else:
                raise Exception("Unknown type", type)
            if not name_child:
                continue
            name = name_child.value
            if name_child is node.children[-1]:
                self.imports[name] = [
                    child.prev_sibling, child]
            else:
                self.imports[name] = [
                    child, child.next_sibling]

    def visit_power(self, node):
        first = node.children[0]
        rest = node.children[1:]
        type = type_name(first)
        if type == "AWAIT":
            first = node.children[1]
            rest = node.children[2:]
        elif type == "atom":
            return self.generic_visit(node)
        name = first.value
        self.names[name] = node
        ended = False
        for child in rest:
            if type_name(child) != "trailer" or \
                type_name(child.children[0]) != "DOT":
                ended = True
            if ended:
                self.generic_visit(child)
            else:
                name += "." + child.children[1].value
                self.names[name] = child

    def visit_trailer(self, node):
        is_dotted = node.children[0].value == "."
        if is_dotted:
            self.in_trailer += 1
        self.generic_visit(node)
        if is_dotted:
            self.in_trailer -= 1
        self.generic_visit(node)

    def visit_NAME(self, node):
        if self.in_trailer == 0:
            self.names[node.value] = node

    def visit_dotted_name(self, node):
        name = ""
        for child in node.children:
            name += child.value
            if type_name(child) == "DOT":
                continue
            self.names[name] = node

    def remove_import(self, node):
        if not node:
            return
        prefix = node.prefix
        if node.next_sibling:
            node.next_sibling.prefix = prefix + node.next_sibling.prefix
        node.remove()

    def visit_ENDMARKER(self, node):
        for name in self.imports:
            if name in self.names:
                continue
            for node in self.imports[name]:
                self.remove_import(node)
        for node in self.multi_imports:
            import_as_node = node.children[-1]
            if type_name(import_as_node) == "RPAR":
                import_as_node = import_as_node.prev_sibling
            if len(import_as_node.children):
                continue
            self.remove_import(node.parent)
