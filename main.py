import argparse
import importlib
import samples
import sys
from parser import parse_any


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visitor", required=True)
    parser.add_argument("path", action="append")
    args = parser.parse_args()

    try:
        visitor_cls = importlib.import_module("samples.{}".format(args.visitor))
    except ModuleNotFoundError:
        print("Unknown refactoring:", args.visitor)
        sys.exit(1)

    for path in args.path:
        for filename, path, tree in parse_any(path):
            print("Refactoring", filename)
            visitor = visitor_cls.Visitor()
            visitor.visit(tree)
            with open(path, "w") as f:
                f.write(str(tree))


if __name__ == "__main__":
    main()
