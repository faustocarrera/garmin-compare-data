#!/usr/bin/env python
"""
Garmin utils
"""

from os import path
from os import listdir


def get_path(file_path, folder=None):
    "Get full folder path"
    source_path = path.dirname(path.realpath(file_path))
    return path.realpath(path.join(source_path, folder)) if folder else source_path


def get_files(folder):
    "List files in a directory"
    return [f for f in listdir(folder) if path.isfile(path.join(folder, f))]
