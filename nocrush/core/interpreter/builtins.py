"""
Built-in functions and constants for the NooCrush interpreter.
"""
from typing import Any, Dict, List, Optional, Callable, TypeVar, Sequence, Iterable, Iterator, Union
import math
import random
import time
import sys
import os
import io
import json
import inspect
from datetime import datetime
from functools import wraps

from noocrush.core.interpreter.error import (
    TypeError, ValueError, IndexError, KeyError, 
    ZeroDivisionError, AttributeError, ImportError
)
from noocrush.core.interpreter.utils import (
    is_iterable, is_hashable, stringify, format_value,
    get_length, get_item, set_item, is_truthy, is_equal,
    check_type, convert_type, is_close, clamp
)

# Type variable for generic type hints
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Built-in constants
BUILTIN_CONSTANTS = {
    'True': True,
    'False': False,
    'None': None,
    'NotImplemented': NotImplemented,
    'Ellipsis': Ellipsis,
    '__name__': '__main__',
    '__file__': None,
    '__builtins__': {},
}

# Type checking and conversion functions

def builtin_type(obj: Any = None) -> type:
    """Return the type of an object or create a new type."""
    if obj is None:
        return type(None)
    return type(obj)


def builtin_isinstance(obj: Any, classinfo: type) -> bool:
    """Return whether an object is an instance of a class or of a subclass thereof."""
    return isinstance(obj, classinfo)


def builtin_issubclass(cls: type, classinfo: type) -> bool:
    """Return whether 'cls' is a derived from another class or is the same class."""
    return issubclass(cls, classinfo)


def builtin_callable(obj: Any) -> bool:
    """Return whether the object is callable."""
    return callable(obj)


def builtin_hasattr(obj: Any, name: str) -> bool:
    """Return whether the object has an attribute with the given name."""
    return hasattr(obj, name)


def builtin_getattr(obj: Any, name: str, default: Any = None) -> Any:
    """Get a named attribute from an object; getattr(x, 'y') is equivalent to x.y."""
    return getattr(obj, name, default)

def builtin_setattr(obj: Any, name: str, value: Any) -> None:
    """Sets the named attribute on the given object to the specified value."""
    setattr(obj, name, value)

def builtin_delattr(obj: Any, name: str) -> None:
    """Deletes the named attribute from the given object."""
    delattr(obj, name)

# String and representation functions

def builtin_str(obj: Any = '') -> str:
    """Return a string version of an object."""
    return str(obj)


def builtin_repr(obj: Any) -> str:
    """Return a string containing a printable representation of an object."""
    return repr(obj)

def builtin_format(value: Any, format_spec: str = '') -> str:
    """Convert a value to a formatted representation."""
    return format(value, format_spec)


def builtin_ascii(obj: Any) -> str:
    """Return a string containing a printable representation of an object, escaping non-ASCII characters."""
    return ascii(obj)

# Numeric functions

def builtin_int(x: Any = 0, base: int = 10) -> int:
    """Convert a number or string to an integer, or return 0 if no arguments are given."""
    if isinstance(x, str):
        return int(x, base)
    return int(x)


def builtin_float(x: Any = 0.0) -> float:
    """Convert a string or number to a floating point number, if possible."""
    return float(x)


def builtin_bool(x: Any = False) -> bool:
    """Convert a value to a Boolean, using the standard truth testing procedure."""
    return bool(x)


def builtin_abs(x: Any) -> Any:
    """Return the absolute value of a number."""
    return abs(x)


def builtin_divmod(a: Any, b: Any) -> tuple:
    """Return the pair (a // b, a % b)."""
    return divmod(a, b)

def builtin_pow(x: Any, y: Any, z: Optional[Any] = None) -> Any:
    """Return x to the power y; if z is present, return x to the power y, modulo z."""
    return pow(x, y, z) if z is not None else pow(x, y)


def builtin_round(number: Any, ndigits: Optional[int] = None) -> Any:
    """Round a number to a given precision in decimal digits."""
    if ndigits is not None:
        return round(number, ndigits)
    return round(number)


# Sequence and collection functions

def builtin_len(obj: Any) -> int:
    """Return the length (the number of items) of an object."""
    try:
        return len(obj)
    except TypeError as e:
        raise TypeError(f"object of type '{type(obj).__name__}' has no len()") from e


def builtin_range(start: int, stop: Optional[int] = None, step: int = 1) -> range:
    """
    Return an object that produces a sequence of integers from start (inclusive) to stop (exclusive) by step.
    
    range(i, j) produces i, i+1, i+2, ..., j-1.
    start defaults to 0, and stop is omitted!
    When step is given, it specifies the increment (or decrement).
    """
    if stop is None:
        return range(0, start, step or 1)
    return range(start, stop, step)


def builtin_enumerate(iterable: Iterable, start: int = 0) -> Iterator[tuple]:
    """Return an enumerate object."""
    return enumerate(iterable, start)


def builtin_zip(*iterables: Iterable) -> Iterator[tuple]:
    """Return a zip object whose .__next__() method returns a tuple."""
    return zip(*iterables)


def builtin_sorted(iterable: Iterable, *, key=None, reverse: bool = False) -> List[Any]:
    """Return a new list containing all items from the iterable in ascending order."""
    return sorted(iterable, key=key, reverse=reverse)


def builtin_reversed(sequence: Sequence) -> Iterator[Any]:
    """Return a reverse iterator over the values of the given sequence."""
    return reversed(sequence)


def builtin_all(iterable: Iterable) -> bool:
    """Return True if all elements of the iterable are true (or if the iterable is empty)."""
    return all(iterable)


def builtin_any(iterable: Iterable) -> bool:
    """Return True if any element of the iterable is true. If the iterable is empty, return False."""
    return any(iterable)


def builtin_min(*args, key=None, default=None) -> Any:
    """Return the smallest item in an iterable or the smallest of two or more arguments."""
    if len(args) == 1:
        return min(args[0], key=key, default=default)
    if default is not None:
        raise TypeError("Cannot specify a default for min() with multiple positional arguments")
    return min(args, key=key)


def builtin_max(*args, key=None, default=None) -> Any:
    """Return the largest item in an iterable or the largest of two or more arguments."""
    if len(args) == 1:
        return max(args[0], key=key, default=default)
    if default is not None:
        raise TypeError("Cannot specify a default for max() with multiple positional arguments")
    return max(args, key=key)


def builtin_sum(iterable: Iterable, start: Any = 0) -> Any:
    """Sums start and the items of an iterable from left to right and returns the total."""
    return sum(iterable, start)

# I/O functions

def builtin_print(*values: Any, sep: str = ' ', end: str = '\n', file=None, flush: bool = False) -> None:
    """Print values to a stream, or to sys.stdout by default."""
    if file is None:
        file = sys.stdout
    print(*values, sep=sep, end=end, file=file, flush=flush)


def builtin_input(prompt: str = '') -> str:
    """Read a string from standard input. The trailing newline is stripped."""
    return input(prompt)

# Object and class functions

def builtin_hasattr(obj: Any, name: str) -> bool:
    """Return whether the object has an attribute with the given name."""
    return hasattr(obj, name)

def builtin_getattr(obj: Any, name: str, default: Any = None) -> Any:
    """Get a named attribute from an object; getattr(x, 'y') is equivalent to x.y."""
    return getattr(obj, name, default)

def builtin_setattr(obj: Any, name: str, value: Any) -> None:
    """Sets the named attribute on the given object to the specified value."""
    setattr(obj, name, value)

def builtin_delattr(obj: Any, name: str) -> None:
    """Deletes the named attribute from the given object."""
    delattr(obj, name)

def builtin_dir(obj: Any = None) -> List[str]:
    """Return a list of names in the current local scope or a list of attributes of an object."""
    if obj is None:
        import inspect
        frame = inspect.currentframe()
        try:
            return list(frame.f_back.f_locals.keys())
        finally:
            del frame
    return dir(obj)

def builtin_vars(obj: Any = None) -> dict:
    """Return the __dict__ attribute for a module, class, instance, or any other object with a __dict__."""
    if obj is None:
        import inspect
        frame = inspect.currentframe()
        try:
            return frame.f_back.f_locals.copy()
        finally:
            del frame
    return vars(obj)

# Type conversion functions

def builtin_list(iterable: Optional[Iterable] = None) -> list:
    """Return a new list containing items from the iterable."""
    if iterable is None:
        return []
    return list(iterable)


def builtin_dict(mapping: Any = None, **kwargs) -> dict:
    """Create a new dictionary."""
    if mapping is None:
        return dict(**kwargs)
    return dict(mapping, **kwargs)

def builtin_tuple(iterable: Optional[Iterable] = None) -> tuple:
    """Return a tuple with items from the iterable."""
    if iterable is None:
        return ()
    return tuple(iterable)

def builtin_set(iterable: Optional[Iterable] = None) -> set:
    """Return a new set object, optionally with elements taken from iterable."""
    if iterable is None:
        return set()
    return set(iterable)

def builtin_frozenset(iterable: Optional[Iterable] = None) -> frozenset:
    """Return a new frozenset object, optionally with elements taken from iterable."""
    if iterable is None:
        return frozenset()
    return frozenset(iterable)

# Math functions

def builtin_abs(x: Any) -> Any:
    """Return the absolute value of a number."""
    return abs(x)

def builtin_divmod(a: Any, b: Any) -> tuple:
    """Return the pair (a // b, a % b)."""
    return divmod(a, b)

def builtin_pow(x: Any, y: Any, z: Optional[Any] = None) -> Any:
    """Return x to the power y; if z is present, return x to the power y, modulo z."""
    return pow(x, y, z) if z is not None else pow(x, y)

def builtin_round(number: Any, ndigits: Optional[int] = None) -> Any:
    """Round a number to a given precision in decimal digits."""
    if ndigits is not None:
        return round(number, ndigits)
    return round(number)

# Helper function to create built-ins dictionary

def create_builtins() -> Dict[str, Any]:
    """
    Create a dictionary of built-in functions and constants.
    
    Returns:
        A dictionary mapping names to built-in functions and constants.
    """
    builtins = {}
    
    # Add built-in functions
    builtins.update({
        # Type checking and conversion
        'type': builtin_type,
        'isinstance': builtin_isinstance,
        'issubclass': builtin_issubclass,
        'callable': builtin_callable,
        'hasattr': builtin_hasattr,
        'getattr': builtin_getattr,
        'setattr': builtin_setattr,
        'delattr': builtin_delattr,
        
        # String and representation
        'str': builtin_str,
        'repr': builtin_repr,
        'format': builtin_format,
        'ascii': builtin_ascii,
        
        # Numeric functions
        'int': builtin_int,
        'float': builtin_float,
        'bool': builtin_bool,
        'abs': builtin_abs,
        'divmod': builtin_divmod,
        'pow': builtin_pow,
        'round': builtin_round,
        
        # Sequence and collection functions
        'len': builtin_len,
        'range': builtin_range,
        'enumerate': builtin_enumerate,
        'zip': builtin_zip,
        'sorted': builtin_sorted,
        'reversed': builtin_reversed,
        'all': builtin_all,
        'any': builtin_any,
        'min': builtin_min,
        'max': builtin_max,
        'sum': builtin_sum,
        
        # I/O functions
        'print': builtin_print,
        'input': builtin_input,
        
        # Object and class functions
        'hasattr': builtin_hasattr,
        'getattr': builtin_getattr,
        'setattr': builtin_setattr,
        'delattr': builtin_delattr,
        'dir': builtin_dir,
        'vars': builtin_vars,
        
        # Type conversion functions
        'list': builtin_list,
        'dict': builtin_dict,
        'tuple': builtin_tuple,
        'set': builtin_set,
        'frozenset': builtin_frozenset,
    })
    
    # Add constants
    builtins.update(BUILTIN_CONSTANTS)
    
    # Add math functions and constants
    builtins.update({
        # Math functions
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'round': round,
        'pow': pow,
        'divmod': divmod,
        'bin': bin,
        'oct': oct,
        'hex': hex,
        'chr': chr,
        'ord': ord,
        'hash': hash,
        'id': id,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'callable': callable,
        'len': len,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'sorted': sorted,
        'reversed': reversed,
        'all': all,
        'any': any,
        'map': map,
        'filter': filter,
        'iter': iter,
        'next': next,
        'slice': slice,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'tuple': tuple,
        'dict': dict,
        'set': set,
        'frozenset': frozenset,
        'type': type,
        'object': object,
        'property': property,
        'classmethod': classmethod,
        'staticmethod': staticmethod,
        'super': super,
        'hasattr': hasattr,
        'getattr': getattr,
        'setattr': setattr,
        'delattr': delattr,
        'dir': dir,
        'vars': vars,
        'globals': globals,
        'locals': locals,
        'breakpoint': breakpoint,
        'compile': compile,
        'eval': eval,
        'exec': exec,
        'open': open,
        'print': print,
        'input': input,
        'repr': repr,
        'ascii': ascii,
        'format': format,
        'memoryview': memoryview,
        'bytearray': bytearray,
        'bytes': bytes,
    })
    
    # Add math module functions and constants
    builtins.update({
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
        'nan': math.nan,
        'ceil': math.ceil,
        'floor': math.floor,
        'trunc': math.trunc,
        'factorial': math.factorial,
        'gcd': math.gcd,
        'lcm': getattr(math, 'lcm', lambda a, b: abs(a * b) // math.gcd(a, b) if a and b else 0),
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'hypot': math.hypot,
        'degrees': math.degrees,
        'radians': math.radians,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'asinh': math.asinh,
        'acosh': math.acosh,
        'atanh': math.atanh,
        'erf': math.erf,
        'erfc': math.erfc,
        'gamma': math.gamma,
        'lgamma': math.lgamma,
        'isfinite': math.isfinite,
        'isinf': math.isinf,
        'isnan': math.isnan,
    })
    
    # Add random module functions
    builtins.update({
        'random': random.random,
        'uniform': random.uniform,
        'randint': random.randint,
        'randrange': random.randrange,
        'choice': random.choice,
        'shuffle': random.shuffle,
        'sample': random.sample,
        'seed': random.seed,
        'getrandbits': random.getrandbits,
    })
    
    # Add time functions
    builtins.update({
        'time': time.time,
        'sleep': time.sleep,
        'ctime': time.ctime,
        'gmtime': time.gmtime,
        'localtime': time.localtime,
        'mktime': time.mktime,
        'strftime': time.strftime,
        'strptime': time.strptime,
        'time_ns': time.time_ns,
        'monotonic': time.monotonic,
        'monotonic_ns': time.monotonic_ns,
        'perf_counter': time.perf_counter,
        'perf_counter_ns': time.perf_counter_ns,
        'process_time': time.process_time,
        'process_time_ns': time.process_time_ns,
        'thread_time': time.thread_time,
        'thread_time_ns': time.thread_time_ns,
        'timezone': time.timezone,
        'tzname': time.tzname,
        'daylight': time.daylight,
    })
    
    return builtins
