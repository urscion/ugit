"""In charge of parsing and processing user input."""

import argparse
import pathlib
import sys
import textwrap

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

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('--message', '-m', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', nargs='?')

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


def commit(args) -> None:
    print(base.commit(args.message))


def log(args) -> None:
    oid = args.oid or data.get_HEAD()
    while oid:
        commit = base.get_commit(oid)

        print(f"commit {oid}\n")
        print(textwrap.indent(commit.message, '    '))
        print("")

        oid = commit.parent
