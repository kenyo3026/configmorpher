import json
import yaml
import inspect
import tomllib
from enum import Enum
from pathlib import Path
from dataclasses import is_dataclass, fields, make_dataclass
from typing import Any, Union, NewType, Iterable, Dict, List

from .utils import iterate_and_fetch_dict_value

CallableObj = NewType("CallableObj", Any)


def create_dataclass_from_callable(callable_obj):
    """
    Create a dataclass based on the signature of a callable (function or method).
    """
    if not callable(callable_obj):
        raise TypeError(f'{callable_obj} is not callable.')

    signature = inspect.signature(callable_obj)
    fields_list = []

    for param_name, param in signature.parameters.items():
        if param_name in ('self', 'cls'):
            continue
        param_type = param.annotation if param.annotation is not param.empty else Any
        param_default = param.default if param.default is not param.empty else None
        fields_list.append((param_name, param_type, param_default))

    dataclass_name = f"{callable_obj.__name__}DataClass"
    return make_dataclass(dataclass_name, fields_list)


class ReturnType(Enum):
    DATACLASS = 'dataclass'
    DICT = 'dict'


class ConfigMorpher:
    """
    A class to handle the parsing of dictionaries into dataclass instances.
    This class morphs a given configuration dictionary into specified `callable_obj` formats dynamically.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ConfigMorpher with a configuration dictionary.
        Args:
            config (Dict[str, Any]): The configuration dictionary to morph later.
        """
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary.")
        self.config = config

    @classmethod
    def from_toml(cls, config_path: Path):
        """
        Morph a TOML file and return a ConfigMorpher instance.
        Args:
            config_path (Path): Path to the TOML file.
        Returns:
            ConfigMorpher: An initialized ConfigMorpher instance.
        """
        config_path = Path(config_path)  # Ensure `config_path` is a Path object
        with config_path.open("rb") as f:  # Use Path's open method
            config_data = tomllib.load(f)
        return cls(config_data)

    @classmethod
    def from_json(cls, config_path: Path):
        """
        Morph a JSON file and return a ConfigMorpher instance.
        Args:
            config_path (Path): Path to the JSON file.
        Returns:
            ConfigMorpher: An initialized ConfigMorpher instance.
        """
        config_path = Path(config_path)  # Ensure `config_path` is a Path object
        with config_path.open("rb") as f:  # Use Path's open method
            config_data = json.load(f)
        return cls(config_data)

    @classmethod
    def from_yaml(cls, config_path: Path):
        """
        Morph a YAML file and return a ConfigMorpher instance.
        Args:
            config_path (Path): Path to the YAML file.
        Returns:
            ConfigMorpher: An initialized ConfigMorpher instance.
        """
        config_path = Path(config_path)  # Ensure `config_path` is a Path object
        with config_path.open("r", encoding="utf-8") as f:  # Use Path's open method
            config_data = yaml.safe_load(f)
        return cls(config_data)

    def morph(
        self,
        callable_obj: Union[CallableObj, Iterable[CallableObj]],
        start_from: Union[str, List[str]] = None,
        allow_extra_keys: bool = True,
        return_type: ReturnType = ReturnType.DICT,
        return_config_keys_only: bool = True,
    ):
        """
        Dynamically morph the stored configuration dictionary into specified callable_obj formats.

        Args:
            callable_obj (Union[CallableObj, Iterable[CallableObj]]): Schema(s) to morph against.
            start_from (Union[str, List[str]], optional): Sub-key(s) to start parsing from. Defaults to None.
            allow_extra_keys (bool, optional): Allow keys in the config that aren't used. Defaults to True.
            return_type (ReturnType, optional): Specifies the return type: 'dataclass' or 'dict'. Defaults to ReturnType.DICT.
            return_config_keys_only (bool, optional): Include only config keys if return type is 'dict'. Defaults to True.

        Raises:
            TypeError: If `callable_obj` is invalid or uncallable.
            ValueError: If unused keys exist and `allow_extra_keys` is False.

        Returns:
            Union[Any, Tuple[Any, ...]]:
                A single morphd schema instance or a tuple of schema instances.
        """
        # Navigate into the nested config if `start_from` is specified
        config = self.config
        if start_from:
            config = iterate_and_fetch_dict_value(config, start_from)

        # Ensure `callable_obj` is iterable
        if not isinstance(callable_obj, Iterable):
            callable_obj = [callable_obj]

        outputs, unused_keys = [], set(config.keys())

        for schema in callable_obj:
            if is_dataclass(schema):
                # Handle dataclass schemas
                keys = {f.name for f in fields(schema) if f.init}
                inputs = {k: v for k, v in config.items() if k in keys}
                unused_keys.difference_update(inputs.keys())
                output = schema(**inputs)

            elif inspect.isclass(schema) and '__init__' in schema.__dict__:
                # Handle classes with constructors
                data_class = create_dataclass_from_callable(schema.__init__)
                inputs = {k: v for k, v in config.items() if k in data_class.__annotations__}
                unused_keys.difference_update(inputs.keys())
                output = data_class(**inputs)

            elif inspect.ismethod(schema) or inspect.isfunction(schema):
                # Handle pure functions
                data_class = create_dataclass_from_callable(schema)
                inputs = {k: v for k, v in config.items() if k in data_class.__annotations__}
                unused_keys.difference_update(inputs.keys())
                output = data_class(**inputs)

            else:
                raise TypeError(f'{schema} is not a valid type.')

            # Handle the return type logic
            if return_type in [ReturnType.DATACLASS, ReturnType.DATACLASS.value]:
                outputs.append(output)
            elif return_type in [ReturnType.DICT, ReturnType.DICT.value]:
                output_dict = output.__dict__
                if return_config_keys_only:
                    output_dict = {k: output_dict[k] for k in output_dict if k in config}
                outputs.append(output_dict)
            else:
                raise ValueError(f"Invalid return_type: {return_type}. Choose from: {[rtype.value for rtype in ReturnType]}.")

        # Validate unused keys if disallowed
        if not allow_extra_keys and unused_keys:
            raise ValueError(f"Some keys are not used by any schema: {sorted(unused_keys)}")

        # Return outputs based on number of schemas
        if len(outputs) == 0:
            return None
        if len(outputs) == 1:
            return outputs[0]
        return tuple(outputs)


if __name__ == "__main__":
    import openai

    config_data = {
        'openai': {
            'base_url': 'http: //XX.XX.XX.XX:XXXX/v1',
            'api_key': 'empty',
            'chat': {
                'completions': {
                    'model': 'meta-llama/Llama-3.1-8B-Instruct',
                    'max_tokens': 4096,
                    'temperature': 0.0,
                }
            }
        },
    }

    # Test Case 1: Manually load config.toml and initialize ConfigMorpher
    print("Test Case 1: Manual Initialization with Config Data")
    config_morpher = ConfigMorpher(config_data)
    openai_config = config_morpher.morph(openai.OpenAI, start_from='openai', return_type='dict')
    openai_client = openai.OpenAI(**openai_config)
    print(openai_config)
    print()

    # Test Case 2: Morph nested configuration for openai.chat.completions.create
    print("Test Case 2: Morph Nested Configuration for Chat Completions")
    config_morpher = ConfigMorpher(config_data)
    openai_config = config_morpher.morph(
        openai_client.chat.completions.create,
        start_from='openai.chat.completions',
        return_type='dict'
    )
    print(openai_config)
    print()