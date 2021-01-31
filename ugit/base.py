"""Basic higher-level logic of ugit"""
import pathlib
from typing import Generator, Tuple

from . import data


def write_tree(directory: str = '.') -> str:
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


def read_tree(tree_oid: str):
    for path, oid in get_tree(tree_oid, base_path='.').items():
        file = pathlib.Path(path)
        file.parent.mkdir(exist_ok=True)
        file.write_bytes(data.get_object(oid))


def is_ignored(path: str):
    return '.ugit' in pathlib.Path(path).parts
