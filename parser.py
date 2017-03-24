import ast
import os
import sys
from lib2to3 import pygram
from lib2to3 import pytree
from lib2to3.pgen2 import driver
from lib2to3.pgen2 import parse
from lib2to3.pgen2 import token

_GRAMMAR_FOR_PY3 = pygram.python_grammar_no_print_statement.copy()
del _GRAMMAR_FOR_PY3.keywords['exec']

_GRAMMAR_FOR_PY2 = pygram.python_grammar.copy()
del _GRAMMAR_FOR_PY2.keywords['nonlocal']


def parse_string(code):
    """Parse the given code to a lib2to3 pytree.
    Arguments:
      code: a string with the code to parse.
    Raises:
      SyntaxError if the code is invalid syntax.
      parse.ParseError if some other parsing failure.
    Returns:
      The root node of the parsed tree.
    """
    try:
        parser_driver = driver.Driver(_GRAMMAR_FOR_PY3, convert=pytree.convert)
        tree = parser_driver.parse_string(code, debug=False)
    except parse.ParseError:
        try:
            parser_driver = driver.Driver(_GRAMMAR_FOR_PY2,
              convert=pytree.convert)
            tree = parser_driver.parse_string(code, debug=False)
        except parse.ParseError:
            try:
                ast.parse(code)
            except SyntaxError as e:
                raise e
            else:
                raise
    return tree


def parse_file(filename):
    code = open(filename).read()
    if not code.endswith("\n"):
        code += "\n"
    return parse_string(code)


def parse_dir(dir):
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            if filename.endswith(".py"):
                yield (filename, parse_file(
                    os.path.join(dirpath, filename)))


def parse_any(arg):
    if os.path.isfile(arg):
        yield (arg, parse_file(arg))
    elif os.path.isdir(arg):
        yield from parse_dir(arg)
    else:
        print("Ignoring", arg)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        for filename, tree in parse_any(arg):
            print(filename, tree is not None)

