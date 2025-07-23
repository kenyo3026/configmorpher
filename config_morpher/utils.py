from typing import Any, List, Union


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
        to = to.split('.')
    elif isinstance(to, list):
        if not to:
            raise ValueError("The provided `to` list is empty.")

    for key in to:
        if not isinstance(cursor, dict):
            raise ValueError(f"The nested structure is invalid: expected dictionary at key '{key}', "
                             f"but got {type(cursor).__name__}.")
        cursor = cursor.get(key)
        if cursor is None:
            raise ValueError(f"Key '{key}' not found in the cursor dictionary.")
    return cursor