"""In charge of parsing and processing user input."""

import argparse
import pathlib
import sys

from . import base
from . import data


def main() -> None:
    args = parse_args()
    args.func(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser('hash-object')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file')

    cat_file_parser = commands.add_parser('cat-file')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('object')

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree')

    return parser.parse_args()


def init(args) -> None:
    data.init()
    print(f"Initialized empty ugit repository in {pathlib.Path.cwd() / data.GIT_DIR}")


def hash_object(args) -> None:
    path = pathlib.Path(args.file)
    print(data.hash_object(path.read_bytes))


def cat_file(args) -> None:
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))


def write_tree(args) -> None:
    print(base.write_tree())


def read_tree(args) -> None:
    base.read_tree(args.tree)
