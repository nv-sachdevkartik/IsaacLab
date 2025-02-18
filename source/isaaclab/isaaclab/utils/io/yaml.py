# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Utilities for file I/O with yaml."""

import os
import yaml

from isaaclab.utils import class_to_dict


def load_yaml(filename: str) -> dict:
    """Loads an input PKL file safely.

    Args:
        filename: The path to pickled file.

    Raises:
        FileNotFoundError: When the specified file does not exist.

    Returns:
        The data read from the input file.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    with open(filename) as f:
        data = yaml.full_load(f)
    return data


def dump_yaml(filename: str, data: dict | object, sort_keys: bool = False):
    """Saves data into a YAML file safely.

    Note:
        The function creates any missing directory along the file's path.

    Args:
        filename: The path to save the file at.
        data: The data to save either a dictionary or class object.
        sort_keys: Whether to sort the keys in the output file. Defaults to False.
    """
    # check ending
    if not filename.endswith("yaml"):
        filename += ".yaml"
    # create directory
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    # convert data into dictionary
    if not isinstance(data, dict):
        data = class_to_dict(data)

    # Create custom dumper with better representations
    class CustomDumper(yaml.SafeDumper):
        pass

    # Register custom representers
    CustomDumper.add_representer(tuple, represent_tuple)
    CustomDumper.add_representer(slice, represent_slice)
    CustomDumper.ignore_aliases = lambda *args: True  # Prevent alias references

    # save data
    with open(filename, "w") as f:
        yaml.dump(
            data, f, Dumper=CustomDumper, default_flow_style=False, sort_keys=sort_keys
        )


def represent_tuple(dumper: yaml.Dumper, data: tuple) -> yaml.Node:
    """Convert Python tuple to YAML sequence."""
    return dumper.represent_sequence("tag:yaml.org,2002:seq", list(data))


def represent_slice(dumper: yaml.Dumper, data: slice) -> yaml.Node:
    """Convert Python slice to YAML null if all attributes are None."""
    if data.start is None and data.stop is None and data.step is None:
        return dumper.represent_scalar("tag:yaml.org,2002:null", "")
    # If not all None, represent as sequence of start:stop:step
    return dumper.represent_sequence(
        "tag:yaml.org,2002:seq", [data.start, data.stop, data.step]
    )
