"""In charge of parsing and processing user input."""

import argparse
import os
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

    return parser.parse_args()


def init(args) -> None:
    data.init()
    print(f"Initialized empty ugit repository in {os.getcwd()}/{data.GIT_DIR}")


def hash_object(args) -> None:
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))


def cat_file(args) -> None:
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))
