import re

from typing import Any, List, Union


def split_by_dot_and_brackets(s:str):
    parts = re.split(r'\.(?![^\[]*\])', s)
    result = []
    for part in parts:
        match = re.match(r'([^\[]+)(\[.*\])?', part)
        if match:
            result.append(match.group(1))
            if match.group(2):
                result.append(match.group(2))
    return result

def check_key_under_brackets(key:str):
    return bool(key.startswith('[') and key.endswith(']'))

def iterate_and_fetch_dict_value(cursor:dict, to:Union[str, List[str]]) -> Any:
    """
    Traverse through a nested dictionary using a specified key path and fetch the corresponding value.

    This function takes a dictionary (`cursor`) and a key path (`to`), either as a string with dot-separated keys or as 
    a list of keys, and navigates through the dictionary to retrieve the value located at the specified path. If any key 
    along the path is not found or the structure is invalid, a `ValueError` is raised.

    Args:
        cursor (dict): 
            The dictionary to traverse. This should be a nested dictionary or a data structure containing dictionaries.
            It must be a valid dictionary object, otherwise an exception will be raised.
        to (Union[str, list]): 
            The key path to the desired value. If given as a string, it should be formatted as dot-separated keys 
            (e.g., `"key1.key2.key3"`). Alternatively, it can be provided as a list of keys (e.g., `["key1", "key2", "key3"]`).
            It must be a non-empty string or list, otherwise an exception will be raised.

    Returns:
        Any: 
            The value found at the specified key path in the dictionary.

    Raises:
        ValueError: 
            If the cursor is not a dictionary.
            If `to` is not a valid key path (e.g., None, empty string, empty list).
            If a key in the path does not exist in the given dictionary, an exception is raised with the message indicating 
            which key was not found.
            If a nested value is not a dictionary during traversal, an exception is raised with an appropriate message.

    Example:
        >>> data = {"a": {"b": {"c": 42}}}
        >>> iterate_and_fetch_value(data, "a.b.c")
        42
        
        >>> iterate_and_fetch_value(data, ["a", "b", "c"])
        42

        >>> iterate_and_fetch_value(data, "a.b.d")
        Traceback (most recent call last):
            ...
        ValueError: Key 'd' not found in the cursor dictionary.
    """
    # Validate `cursor` input
    if not isinstance(cursor, dict):
        raise ValueError("The provided `cursor` must be a dictionary.")

    # Validate `to` input
    if isinstance(to, str):
        if not to.strip():
            raise ValueError("The provided `to` string is empty or invalid.")
        # to = to.split('.')
        to = split_by_dot_and_brackets(to)
    elif isinstance(to, list):
        if not to:
            raise ValueError("The provided `to` list is empty.")

    for key in to:

        if isinstance(cursor, dict):

            if check_key_under_brackets(key):
                raise ValueError(f"Unexpected list-style key '{key}' in dict context.")

            if key not in cursor:
                raise ValueError(f"Key '{key}' not found in the cursor dictionary.")

            cursor = cursor[key]

        elif isinstance(cursor, list):

            if not check_key_under_brackets(key):
                raise ValueError(f"Expected list-style key like '[0]' but got '{key}'.")

            inner = key[1:-1]

            # Case: [index]
            if inner.isdigit():
                idx = int(inner)

                if idx >= len(cursor) or idx < 0:
                    raise IndexError(f"List index {idx} out of range.")

                cursor = cursor[idx]

            # Case: [key=value]
            elif '=' in inner:
                if inner.count('=') != 1:
                    raise ValueError(f"Invalid key=value format: '{key}'")

                inner_key, inner_value = inner.split('=', 1)
                matched = False
                for _dict in cursor:
                    if isinstance(_dict, dict) and _dict.get(inner_key) == inner_value:
                        cursor = _dict
                        matched = True
                        break

                if not matched:
                    raise ValueError(f"No item in list matches condition [{inner_key}={inner_value}]")

        else:
            raise ValueError(f"Cannot traverse into type '{type(cursor).__name__}' with key '{key}'.")

    return cursor