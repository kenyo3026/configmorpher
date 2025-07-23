"""
ConfigMorpher - A lightweight and powerful Python configuration morpher
"""

__version__ = "0.1.0"
__author__ = "Kenyo 3026"
__email__ = "kenyo3026@gmail.com"

from .morpher import ConfigMorpher, ReturnType, create_dataclass_from_callable
from .utils import iterate_and_fetch_dict_value

# Define the public API
__all__ = [
    "ConfigMorpher",
    "ReturnType",
    "create_dataclass_from_callable",
    "iterate_and_fetch_dict_value",
]