from lib2to3.pytree import type_repr
from lib2to3.pgen2.tokenize import tok_name


def to_json(node):
    json = {
        "prefix": node.prefix,
        "lineno": node.get_lineno(),
    }
    if node.type in tok_name:
        json["type"] = tok_name[node.type]
        json["is_terminal"] = True
    else:
        json["type"] = type_repr(node.type)
        json["is_terminal"] = False
    if hasattr(node, "value"):
        json["value"] = node.value
    if node.children:
        json["children"] = list(map(to_json, node.children))
    return json
