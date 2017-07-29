# prefactor
This is a tool that allows developers to write AST-based refactorings. It uses `lib2to3` to convert source code to an AST, run visitors over it to modify the tree, and convert the tree back into source code.

## Usage

```
python3 main.py --visitor <visitor> <path>
```

## Writing a visitor

This comes with a Flask app that makes it really easy to write visitors. To use it, just start the app and open it in a browser:
```
python3 app.py
```
![screenshot](https://raw.githubusercontent.com/banga/prefactor/master/screenshot.png)

Paste some Python source code into the first box. The second box should show you the parsed AST. As you move the cursor in the source code, it will highlight parts of the AST generated from the source closest to your cursor.

Now you can start writing your visitor in the third box. The app expects a `Visitor` class that extends the `NodeVisitor` class, which works exactly like the [ast.NodeVisitor](https://docs.python.org/2/library/ast.html#ast.NodeVisitor) class, with the exception that you can modify nodes in-place.

Try pasting this:

```python
from visitor import NodeVisitor

class Visitor(NodeVisitor):
    def visit_NAME(self, node):
        parts = node.value.split("_")
        parts = [parts[0]] + list(map(lambda x: x.title(), parts[1:]))
        node.value = "".join(parts)
```

You should see all snake_case variable names converted to camelCase in the last box. You can also try the sample visitors in the [visitors/](https://github.com/banga/prefactor/tree/master/visitors) directory.

## Why `lib2to3`

The AST returned by Python's `ast` module is lossy — it strips out information necessary for recreating the source code with the correct whitespace and comments. The AST returned by `lib2to3` is more low-level, so it retains all of the information required to regenerate the source code faithfully. The downside is that the visitors on this AST end up being more complex than those based on the `ast` module.

## Inspiration
- [2to3](https://docs.python.org/3.0/library/2to3.html)
- [yapf](https://github.com/google/yapf)
- [mypy](https://github.com/python/mypy)
