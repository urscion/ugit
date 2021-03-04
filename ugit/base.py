"""Basic higher-level logic of ugit"""
import pathlib
import os
from typing import Generator
import itertools
import operator
from dataclasses import dataclass

from . import data


@dataclass
class Commit:
    tree: str
    parent: str
    message: str


def write_tree(directory: str = '.') -> str:
    """Write tree to objects

    Args:
        directory: Directory path
    Returns:
        OID of tree
    """
    entries = []
    for entry in pathlib.Path(directory).iterdir():
        full = pathlib.Path(directory) / entry.name
        if is_ignored(full.resolve()):
            continue
        if entry.is_file():
            type_ = 'blob'
            oid = data.hash_object(full.read_bytes())
        elif entry.is_dir():
            type_ = 'tree'
            oid = write_tree(full)
        entries.append((full.name, oid, type_))

    tree = ''.join(f"{type_} {oid} {name}\n" for name, oid, type_ in sorted(entries))
    return data.hash_object(tree.encode(), 'tree')


def _iter_tree_entries(oid: str) -> Generator[str, str, str]:
    """Generator that takes an OID of a tree, tokenizes it line-by-line, and
       yields the raw string values.
    """
    if not oid:
        return
    tree = data.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(' ', 2)
        yield type_, oid, name


def get_tree(oid: str, base_path: str = '') -> dict:
    """Recursively parse a tree into a dictionary of paths and OIDs"""
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = pathlib.Path(base_path) / name
        if type_ == 'blob':
            result[str(path)] = oid
        elif type_ == 'tree':
            result.update(get_tree(oid, f"{str(path)}"))
        else:
            assert False, f"Unknown tree entry {type_}"
    return result


def _empty_current_directory():
    # Start from the bottom to allow deletion of directories
    for root, dirnames, filenames in os.walk(pathlib.Path('.'), topdown=False):
        for fname in filenames:
            path = pathlib.Path(root) / fname
            if is_ignored(path) or not path.is_file():
                continue
            path.unlink()
        for dname in dirnames:
            path = pathlib.Path(root) / dname
            if is_ignored(path):
                continue
            try:
                path.rmdir()
            except (FileNotFoundError, OSError):
                # Deletion might fail if the dir contains ignored files, so OK
                print(f"OK: Failed to delete: {path.resolve()}")
                pass


def read_tree(tree_oid: str):
    _empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path='.').items():
        file = pathlib.Path(path)
        file.parent.mkdir(exist_ok=True)
        file.write_bytes(data.get_object(oid))


def commit(message) -> str:
    """Perform a commit

    Args:
        message: commit message

    Returns:
        OID of commit object
    """
    commit = f"tree {write_tree()}\n"

    HEAD = data.get_HEAD()
    if HEAD:
        commit += f"parent {HEAD}\n"

    commit += '\n'
    commit += f"{message}\n"

    oid = data.hash_object(commit.encode(), 'commit')
    data.set_HEAD(oid)
    return oid


def get_commit(oid: str) -> Commit:
    """Get a commit by OID

    Args:
        oid: OID of the commit object

    Returns:
        Commit object
    """
    parent = None

    commit_data = data.get_object(oid, 'commit').decode()
    lines = iter(commit_data.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(' ', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parent = value
        else:
            assert False, f"Unknown field {key}"

    message = '\n'.join(lines)
    return Commit(tree=tree, parent=parent, message=message)


def is_ignored(path: str):
    return '.ugit' in pathlib.Path(path).parts
