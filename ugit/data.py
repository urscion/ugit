"""Manages the data in .ugit directory.
Here will be the code that actually touches files on disk.
"""

import os
import pathlib
import hashlib

GIT_DIR = pathlib.Path('.ugit')
OBJECTS_DIR = GIT_DIR / 'objects'


def init() -> None:
    os.makedirs(GIT_DIR)
    os.makedirs(OBJECTS_DIR)


def hash_object(data, type_='blob') -> str:
    obj = type_.encode() + b'\x00' + data
    oid = hashlib.sha1(data).hexdigest()
    with open(OBJECTS_DIR / oid, 'wb') as out:
        out.write(obj)
    return oid


def get_object(oid, expected='blob') -> bytes:
    with open(OBJECTS_DIR / oid, 'rb') as f:
        obj = f.read()

    type_, _, content = obj.partition(b'\x00')
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, f"Expected {expected}, got {type_}"
    return content
