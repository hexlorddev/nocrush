""
Utility functions for the NooCrush interpreter.
"""
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, Iterable, Iterator
import math
import operator
import sys
import io
import inspect
from contextlib import redirect_stdout, redirect_stderr

# Type variable for generic type hints
T = TypeVar('T')

# Constants
FLOAT_TOLERANCE = 1e-10

# Type checking functions

def is_truthy(value: Any) -> bool:
    """
    Check if a value is truthy in NooCrush.
    
    Args:
        value: The value to check.
        
    Returns:
        bool: True if the value is truthy, False otherwise.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    if isinstance(value, (list, dict, set, tuple)):
        return len(value) > 0
    return True

def is_equal(a: Any, b: Any) -> bool:
    """
    Compare two values for equality with type coercion.
    
    Args:
        a: First value.
        b: Second value.
        
    Returns:
        bool: True if values are equal, False otherwise.
    """
    # Handle None
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    
    # Handle numbers with tolerance for floating point
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < FLOAT_TOLERANCE
    
    # Handle other types with direct comparison
    return a == b

def is_callable(obj: Any) -> bool:
    """
    Check if an object is callable (function, method, class with __call__, etc.).
    
    Args:
        obj: The object to check.
        
    Returns:
        bool: True if the object is callable, False otherwise.
    """
    return callable(obj)

def is_iterable(obj: Any) -> bool:
    """
    Check if an object is iterable.
    
    Args:
        obj: The object to check.
        
    Returns:
        bool: True if the object is iterable, False otherwise.
    """
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def is_hashable(obj: Any) -> bool:
    """
    Check if an object is hashable (can be used as a dictionary key).
    
    Args:
        obj: The object to check.
        
    Returns:
        bool: True if the object is hashable, False otherwise.
    """
    try:
        hash(obj)
        return True
    except TypeError:
        return False

# String conversion functions

def stringify(value: Any) -> str:
    """
    Convert a value to its string representation.
    
    Args:
        value: The value to convert.
        
    Returns:
        str: The string representation of the value.
    """
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        # Remove trailing .0 for whole numbers
        text = str(value)
        if text.endswith('.0'):
            text = text[:-2]
        return text
    return str(value)

def format_value(value: Any, precision: int = 6) -> str:
    """
    Format a value with specified precision for floating point numbers.
    
    Args:
        value: The value to format.
        precision: Number of decimal places for floating point numbers.
        
    Returns:
        str: The formatted string.
    """
    if isinstance(value, float):
        # Format with specified precision, removing trailing zeros
        formatted = f"{value:.{precision}f}"
        # Remove trailing .0 for whole numbers
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return formatted
    return stringify(value)

# Collection utilities

def get_length(collection: Any) -> int:
    """
    Get the length of a collection (list, string, dict, etc.).
    
    Args:
        collection: The collection to measure.
        
    Returns:
        int: The length of the collection.
        
    Raises:
        TypeError: If the object doesn't have a length.
    """
    try:
        return len(collection)
    except TypeError as e:
        raise TypeError(f"Object of type '{type(collection).__name__}' has no len()") from e

def get_item(collection: Any, key: Any) -> Any:
    """
    Get an item from a collection by key or index.
    
    Args:
        collection: The collection (list, dict, etc.).
        key: The key or index.
        
    Returns:
        The value at the specified key/index.
        
    Raises:
        KeyError: If the key is not found in a dictionary.
        IndexError: If the index is out of range for a sequence.
        TypeError: If the operation is not supported for the type.
    """
    try:
        return collection[key]
    except (KeyError, IndexError, TypeError) as e:
        if isinstance(e, KeyError):
            raise KeyError(f"Key '{key}' not found") from e
        elif isinstance(e, IndexError):
            raise IndexError("Index out of range") from e
        else:
            raise TypeError("Object is not subscriptable") from e

def set_item(collection: Any, key: Any, value: Any) -> None:
    """
    Set an item in a collection by key or index.
    
    Args:
        collection: The collection (list, dict, etc.).
        key: The key or index.
        value: The value to set.
        
    Raises:
        TypeError: If the operation is not supported for the type.
    """
    try:
        collection[key] = value
    except (TypeError, IndexError) as e:
        if isinstance(e, IndexError):
            raise IndexError("Index out of range") from e
        else:
            raise TypeError("Object does not support item assignment") from e

# Function utilities

def get_arity(func: Callable) -> int:
    """
    Get the number of parameters a function accepts.
    
    Args:
        func: The function to inspect.
        
    Returns:
        int: The number of parameters the function accepts.
    """
    if hasattr(func, '__code__'):
        return func.__code__.co_argcount
    elif hasattr(func, 'arity'):
        return func.arity()
    elif callable(func):
        # For built-in functions, we can't easily determine arity
        return 0
    return 0

def call_with_args(func: Callable, args: list) -> Any:
    """
    Call a function with the given arguments.
    
    Args:
        func: The function to call.
        args: Arguments to pass to the function.
        
    Returns:
        The result of the function call.
        
    Raises:
        TypeError: If the function is not callable.
    """
    if not callable(func):
        raise TypeError(f"'{type(func).__name__}' object is not callable")
    return func(*args)

# Error formatting

def format_error(message: str, line: int = None, where: str = "") -> str:
    """
    Format an error message with line number and context.
    
    Args:
        message: The error message.
        line: The line number where the error occurred.
        where: Additional context about where the error occurred.
        
    Returns:
        str: The formatted error message.
    """
    result = []
    if line is not None:
        result.append(f"[line {line}]")
    if where:
        result.append(f" at '{where}'")
    if result:
        result.append(": ")
    result.append(message)
    return "".join(result)

# Type checking and conversion

def check_type(value: Any, expected_type: type, name: str = "value") -> None:
    """
    Check if a value is of the expected type.
    
    Args:
        value: The value to check.
        expected_type: The expected type.
        name: The name of the value (for error messages).
        
    Raises:
        TypeError: If the value is not of the expected type.
    """
    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be {expected_type.__name__}, got {type(value).__name__}")

def convert_type(value: Any, target_type: type, name: str = "value") -> Any:
    """
    Convert a value to the specified type if possible.
    
    Args:
        value: The value to convert.
        target_type: The type to convert to.
        name: The name of the value (for error messages).
        
    Returns:
        The converted value.
        
    Raises:
        ValueError: If the value cannot be converted to the target type.
    """
    if value is None or isinstance(value, target_type):
        return value
    
    try:
        if target_type == bool:
            return bool(value)
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return str(value)
        elif target_type == list:
            return list(value) if is_iterable(value) else [value]
        elif target_type == dict and hasattr(value, 'items'):
            return dict(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to convert {name} to {target_type.__name__}: {e}") from e
    
    raise ValueError(f"Cannot convert {type(value).__name__} to {target_type.__name__}")

# Math utilities

def is_close(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    """
    Check if two floating point numbers are approximately equal.
    
    Args:
        a: First number.
        b: Second number.
        rel_tol: Relative tolerance.
        abs_tol: Absolute tolerance.
        
    Returns:
        bool: True if the numbers are approximately equal.
    """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between a minimum and maximum.
    
    Args:
        value: The value to clamp.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.
        
    Returns:
        float: The clamped value.
    """
    return max(min_val, min(max_val, value))
