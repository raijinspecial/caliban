"""Hypothesis is a library for writing unit tests which are parametrized by
some source of data.
It verifies your code against a wide range of input and minimizes any
failing examples it finds.
"""

from __future__ import absolute_import, division, print_function

from caliban.cloud.core import submit_package, valid_regions

__all__ = [
    "submit_package",
    "valid_regions",
]