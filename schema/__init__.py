import importlib
from transformers.utils import get_json_schema

from .hera import *
from .home_automation import *

__version__ = (1, 0, 0)


def get(module_name: str):
    module = importlib.import_module('.' + module_name, 'schema')
    functions = [attr for attr in dir(module) if not attr.startswith('__')]
    return [get_json_schema(getattr(module, function)) for function in functions]
