import argparse
import importlib
import visitors
import sys
from parser import parse_any


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visitor", required=True)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("path", action="append")
    args = parser.parse_args()

    try:
        visitor_cls = importlib.import_module(
            "visitors.{}".format(args.visitor))
    except ModuleNotFoundError:
        print("Unknown visitor:", args.visitor)
        sys.exit(1)

    for path in args.path:
        for filename, path, tree in parse_any(path):
            if args.verbose:
                print("Reading", filename)
            visitor = visitor_cls.Visitor()
            visitor.visit(tree)
            if not tree.was_changed:
                continue
            print("Refactored", filename)
            with open(path, "w") as f:
                f.write(str(tree))


if __name__ == "__main__":
    main()
