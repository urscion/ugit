"""Manages the data in .ugit directory.
Here will be the code that actually touches files on disk.
"""

import pathlib
import hashlib

GIT_DIR = pathlib.Path('.ugit')
OBJECTS_DIR = GIT_DIR / 'objects'


def init() -> None:
    try:
        GIT_DIR.mkdir()
    except FileExistsError:
        print(f"Ugit directory {GIT_DIR} already exists!")
    try:
        OBJECTS_DIR.mkdir()
    except FileExistsError:
        print(f"Ugit Object Directory {OBJECTS_DIR} already exists!")


def hash_object(data: bytes, type_: str = 'blob') -> str:
    """Hash the type and data and store to the Object Directory

    Args:
        data: File data
        type_: File type

    Returns:
        OID - Object ID
    """
    obj = type_.encode() + b'\x00' + data
    oid = hashlib.sha1(data).hexdigest()
    path = OBJECTS_DIR / oid
    path.write_bytes(obj)
    return oid


def get_object(oid: str, expected: str = 'blob') -> bytes:
    """Return an OIDs content"""
    path = OBJECTS_DIR / oid
    obj = path.read_bytes()

    type_, _, content = obj.partition(b'\x00')
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, f"Expected {expected}, got {type_}"
    return content
