from lib2to3.pytree import type_repr


def to_json(node):
    json = {
        "type": type_repr(node.type),
        "prefix": node.prefix,
        "lineno": node.get_lineno(),
    }
    if hasattr(node, "value"):
        json["value"] = node.value
    if node.children:
        json["children"] = list(map(to_json, node.children))
    return json
