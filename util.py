from lib2to3.pytree import type_repr
from lib2to3.pgen2.tokenize import tok_name


def type_name(node):
    if node.type in tok_name:
        return tok_name[node.type]
    return type_repr(node.type)


def to_json(node):
    json = {
        "prefix": node.prefix,
        "lineno": node.get_lineno(),
        "type": type_name(node),
        "is_terminal": node.type in tok_name
    }
    if hasattr(node, "value"):
        json["value"] = node.value
    if node.children:
        json["children"] = list(map(to_json, node.children))
    return json
