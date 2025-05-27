""
NooCrush Standard Library
"""
from typing import List, Dict, Any, Callable
from ..interpreter import Value, ValueType, Interpreter

def register_stdlib(interpreter: Interpreter) -> None:
    """Register all standard library functions."""
    stdlib = {
        # Math functions
        'abs': (abs_, 1),
        'min': (min_, 2),
        'max': (max_, 2),
        'pow': (pow_, 2),
        'sqrt': (sqrt, 1),
        'floor': (floor, 1),
        'ceil': (ceil, 1),
        'round': (round_, 1),
        'rand': (rand, 0),
        'randint': (randint, 2),
        
        # String functions
        'len': (len_, 1),
        'upper': (upper, 1),
        'lower': (lower, 1),
        'trim': (trim, 1),
        'split': (split, 2),
        'join': (join, 2),
        'contains': (contains, 2),
        'replace': (replace, 3),
        
        # List functions
        'push': (push, 2),
        'pop': (pop, 1),
        'slice': (slice_, 3),
        'map': (map_, 2),
        'filter': (filter_, 2),
        'reduce': (reduce_, 2),
        
        # Type conversion
        'str': (to_str, 1),
        'num': (to_num, 1),
        'bool': (to_bool, 1),
        'list': (to_list, 1),
        
        # I/O
        'print': (print_, -1),  # -1 means variable number of arguments
        'input': (input_, 0),
        'read_file': (read_file, 1),
        'write_file': (write_file, 2),
    }
    
    for name, (func, arity) in stdlib.items():
        interpreter.globals.define(name, Value(ValueType.BUILTIN_FUNCTION, 
            create_native_function(name, func, arity, interpreter)))

def create_native_function(name: str, func: Callable, arity: int, interpreter: Interpreter):
    """Create a native function with the given name and implementation."""
    def wrapper(args: List[Value]) -> Value:
        if arity >= 0 and len(args) != arity:
            raise RuntimeError(f"Expected {arity} arguments but got {len(args)}.")
        try:
            return func(args, interpreter)
        except Exception as e:
            raise RuntimeError(f"Error in {name}: {str(e)}")
    return wrapper

# Math functions
def abs_(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, abs(args[0].value))

def min_(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, min(args[0].value, args[1].value))

def max_(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, max(args[0].value, args[1].value))

def pow_(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, args[0].value ** args[1].value)

def sqrt(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, args[0].value ** 0.5)

def floor(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, int(args[0].value // 1))

def ceil(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, int(-(-args[0].value // 1)))

def round_(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.NUMBER, round(args[0].value))

def rand(args: List[Value], _: Interpreter) -> Value:
    import random
    return Value(ValueType.NUMBER, random.random())

def randint(args: List[Value], _: Interpreter) -> Value:
    import random
    return Value(ValueType.NUMBER, random.randint(int(args[0].value), int(args[1].value)))

# String functions
def len_(args: List[Value], _: Interpreter) -> Value:
    if args[0].type == ValueType.STRING:
        return Value(ValueType.NUMBER, len(args[0].value))
    elif args[0].type == ValueType.LIST:
        return Value(ValueType.NUMBER, len(args[0].value))
    raise RuntimeError("Can only get length of strings and lists.")

def upper(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.STRING, args[0].value.upper())

def lower(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.STRING, args[0].value.lower())

def trim(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.STRING, args[0].value.strip())

def split(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.LIST, [Value(ValueType.STRING, s) for s in args[0].value.split(args[1].value)])

def join(args: List[Value], _: Interpreter) -> Value:
    if args[0].type != ValueType.LIST:
        raise RuntimeError("First argument to join must be a list.")
    return Value(ValueType.STRING, args[1].value.join(str(item.value) for item in args[0].value))

def contains(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.BOOLEAN, args[1].value in args[0].value)

def replace(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.STRING, args[0].value.replace(args[1].value, args[2].value))

# List functions
def push(args: List[Value], _: Interpreter) -> Value:
    if args[0].type != ValueType.LIST:
        raise RuntimeError("First argument to push must be a list.")
    args[0].value.append(args[1])
    return args[0]

def pop(args: List[Value], _: Interpreter) -> Value:
    if args[0].type != ValueType.LIST:
        raise RuntimeError("Argument to pop must be a list.")
    if not args[0].value:
        raise RuntimeError("Cannot pop from an empty list.")
    return args[0].value.pop()

def slice_(args: List[Value], _: Interpreter) -> Value:
    if args[0].type != ValueType.LIST and args[0].type != ValueType.STRING:
        raise RuntimeError("First argument to slice must be a list or string.")
    start = int(args[1].value)
    end = int(args[2].value)
    if args[0].type == ValueType.LIST:
        return Value(ValueType.LIST, args[0].value[start:end])
    else:
        return Value(ValueType.STRING, args[0].value[start:end])

def map_(args: List[Value], interpreter: Interpreter) -> Value:
    if args[0].type != ValueType.LIST:
        raise RuntimeError("First argument to map must be a list.")
    if args[1].type != ValueType.FUNCTION:
        raise RuntimeError("Second argument to map must be a function.")
    
    result = []
    for item in args[0].value:
        result.append(interpreter._call_function(args[1], [item]))
    return Value(ValueType.LIST, result)

def filter_(args: List[Value], interpreter: Interpreter) -> Value:
    if args[0].type != ValueType.LIST:
        raise RuntimeError("First argument to filter must be a list.")
    if args[1].type != ValueType.FUNCTION:
        raise RuntimeError("Second argument to filter must be a function.")
    
    result = []
    for item in args[0].value:
        if interpreter._is_truthy(interpreter._call_function(args[1], [item])):
            result.append(item)
    return Value(ValueType.LIST, result)

def reduce_(args: List[Value], interpreter: Interpreter) -> Value:
    if args[0].type != ValueType.LIST:
        raise RuntimeError("First argument to reduce must be a list.")
    if args[1].type != ValueType.FUNCTION:
        raise RuntimeError("Second argument to reduce must be a function.")
    if not args[0].value:
        raise RuntimeError("Cannot reduce an empty list.")
    
    accumulator = args[0].value[0]
    for item in args[0].value[1:]:
        accumulator = interpreter._call_function(args[1], [accumulator, item])
    return accumulator

# Type conversion
def to_str(args: List[Value], _: Interpreter) -> Value:
    return Value(ValueType.STRING, str(args[0].value))

def to_num(args: List[Value], _: Interpreter) -> Value:
    try:
        return Value(ValueType.NUMBER, float(args[0].value))
    except ValueError:
        raise RuntimeError(f"Cannot convert '{args[0].value}' to number")

def to_bool(args: List[Value], _: Interpreter) -> Value:
    if args[0].type == ValueType.BOOLEAN:
        return args[0]
    if args[0].type == ValueType.NUMBER:
        return Value(ValueType.BOOLEAN, bool(args[0].value))
    if args[0].type == ValueType.STRING:
        return Value(ValueType.BOOLEAN, bool(args[0].value))
    if args[0].type == ValueType.LIST:
        return Value(ValueType.BOOLEAN, bool(args[0].value))
    return Value(ValueType.BOOLEAN, False)

def to_list(args: List[Value], _: Interpreter) -> Value:
    if args[0].type == ValueType.LIST:
        return args[0]
    if args[0].type == ValueType.STRING:
        return Value(ValueType.LIST, [Value(ValueType.STRING, c) for c in args[0].value])
    return Value(ValueType.LIST, [args[0]])

# I/O
def print_(args: List[Value], _: Interpreter) -> Value:
    print(" ".join(str(arg.value) for arg in args))
    return Value(ValueType.NULL, None)

def input_(args: List[Value], _: Interpreter) -> Value:
    if args:
        print(args[0].value, end="")
    return Value(ValueType.STRING, input())

def read_file(args: List[Value], _: Interpreter) -> Value:
    with open(args[0].value, 'r', encoding='utf-8') as f:
        return Value(ValueType.STRING, f.read())

def write_file(args: List[Value], _: Interpreter) -> Value:
    with open(args[0].value, 'w', encoding='utf-8') as f:
        f.write(args[1].value)
    return Value(ValueType.NULL, None)
