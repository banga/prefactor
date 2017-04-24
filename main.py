import argparse
import sys
from parser import parse_any
from samples.remove_unused_imports import Visitor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visitor", default="")
    parser.add_argument("path", action="append")
    args = parser.parse_args()

    for path in args.path:
        for filename, path, tree in parse_any(path):
            print("Refactoring", filename)
            visitor = Visitor()
            visitor.visit(tree)
            with open(path, "w") as f:
                f.write(str(tree))


if __name__ == "__main__":
    main()
