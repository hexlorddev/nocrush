"""
Interpreter for the NooCrush language.
"""
import sys
import math
import random
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum, auto

class ValueType(Enum):
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()
    LIST = auto()
    FUNCTION = auto()
    BUILTIN_FUNCTION = auto()
    STRUCT = auto()
    INSTANCE = auto()

@dataclass
class Value:
    type: ValueType
    value: Any

    def __str__(self):
        if self.type == ValueType.NULL:
            return "null"
        elif self.type == ValueType.BOOLEAN:
            return "true" if self.value else "false"
        elif self.type == ValueType.NUMBER:
            return str(int(self.value) if self.value.is_integer() else self.value)
        return str(self.value)

    def is_truthy(self) -> bool:
        if self.type == ValueType.NULL:
            return False
        if self.type == ValueType.BOOLEAN:
            return self.value
        return True

class Environment:
    def __init__(self, enclosing=None):
        self.values: Dict[str, Value] = {}
        self.enclosing = enclosing
    
    def define(self, name: str, value: Value):
        self.values[name] = value
    
    def get(self, name: str) -> Value:
        if name in self.values:
            return self.values[name]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise RuntimeError(f"Undefined variable '{name}'.")
    
    def assign(self, name: str, value: Value):
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(f"Undefined variable '{name}'.")

class ReturnException(Exception):
    def __init__(self, value: Value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self._init_native_functions()
    
    def _init_native_functions(self):
        # Built-in functions
        self.globals.define("print", Value(ValueType.BUILTIN_FUNCTION, self._print))
        self.globals.define("len", Value(ValueType.BUILTIN_FUNCTION, self._len))
        self.globals.define("input", Value(ValueType.BUILTIN_FUNCTION, self._input))
    
    def _print(self, args: List[Value]) -> Value:
        print(" ".join(str(arg) for arg in args))
        return Value(ValueType.NULL, None)
    
    def _len(self, args: List[Value]) -> Value:
        if len(args) != 1:
            raise RuntimeError(f"Expected 1 argument, got {len(args)}.")
        
        value = args[0]
        if value.type == ValueType.STRING or value.type == ValueType.LIST:
            return Value(ValueType.NUMBER, len(value.value))
        
        raise RuntimeError("Can only get length of strings and lists.")
    
    def _input(self, args: List[Value]) -> Value:
        if args:
            print(args[0].value, end="")
        return Value(ValueType.STRING, input())
    
    def interpret(self, statements: List[Dict]):
        try:
            result = None
            for statement in statements:
                result = self._execute(statement)
            return result
        except RuntimeError as e:
            print(f"Runtime error: {e}")
            return None
    
    def _execute(self, stmt: Dict) -> Value:
        if stmt["type"] == "expression":
            return self._evaluate(stmt["expression"])
        elif stmt["type"] == "print":
            value = self._evaluate(stmt["expression"])
            print(self._stringify(value))
            return Value(ValueType.NULL, None)
        elif stmt["type"] == "var":
            value = self._evaluate(stmt["initializer"]) if "initializer" in stmt else Value(ValueType.NULL, None)
            self.environment.define(stmt["name"], value)
            return value
        elif stmt["type"] == "block":
            return self._execute_block(stmt["statements"])
        elif stmt["type"] == "if":
            if self._is_truthy(self._evaluate(stmt["condition"])):
                return self._execute(stmt["then_branch"])
            elif "else_branch" in stmt:
                return self._execute(stmt["else_branch"])
            return Value(ValueType.NULL, None)
        elif stmt["type"] == "loop":
            while True:
                try:
                    self._execute_block(stmt["body"])
                except BreakException:
                    break
            return Value(ValueType.NULL, None)
        elif stmt["type"] == "function":
            function = Value(ValueType.FUNCTION, stmt)
            self.environment.define(stmt["name"], function)
            return function
        elif stmt["type"] == "return":
            value = self._evaluate(stmt["value"]) if "value" in stmt else Value(ValueType.NULL, None)
            raise ReturnException(value)
        
        raise RuntimeError(f"Unknown statement type: {stmt['type']}")
    
    def _execute_block(self, statements: List[Dict], environment: Environment = None) -> Value:
        previous = self.environment
        try:
            self.environment = environment if environment is not None else Environment(previous)
            result = Value(ValueType.NULL, None)
            for statement in statements:
                result = self._execute(statement)
            return result
        finally:
            self.environment = previous
    
    def _evaluate(self, expr: Dict) -> Value:
        if expr["type"] == "literal":
            if expr["value_type"] == "number":
                return Value(ValueType.NUMBER, float(expr["value"]))
            elif expr["value_type"] == "string":
                return Value(ValueType.STRING, expr["value"])
            elif expr["value_type"] == "boolean":
                return Value(ValueType.BOOLEAN, expr["value"])
            else:
                return Value(ValueType.NULL, None)
        
        elif expr["type"] == "variable":
            return self.environment.get(expr["name"])
        
        elif expr["type"] == "assign":
            value = self._evaluate(expr["value"])
            self.environment.assign(expr["name"], value)
            return value
        
        elif expr["type"] == "binary":
            left = self._evaluate(expr["left"])
            right = self._evaluate(expr["right"])
            
            operator = expr["operator"].lexeme
            
            if operator == "+":
                if left.type == ValueType.NUMBER and right.type == ValueType.NUMBER:
                    return Value(ValueType.NUMBER, left.value + right.value)
                elif left.type == ValueType.STRING and right.type == ValueType.STRING:
                    return Value(ValueType.STRING, left.value + right.value)
                else:
                    raise RuntimeError("Operands must be two numbers or two strings.")
            
            # Other binary operators...
            
            raise RuntimeError(f"Unknown operator: {operator}")
        
        elif expr["type"] == "call":
            callee = self._evaluate(expr["callee"])
            arguments = [self._evaluate(arg) for arg in expr["arguments"]]
            
            if callee.type == ValueType.BUILTIN_FUNCTION:
                return callee.value(arguments)
            
            raise RuntimeError("Can only call functions and methods.")
        
        raise RuntimeError(f"Unknown expression type: {expr['type']}")
    
    def _is_truthy(self, value: Value) -> bool:
        if value.type == ValueType.NULL:
            return False
        if value.type == ValueType.BOOLEAN:
            return value.value
        return True
    
    def _stringify(self, value: Value) -> str:
        if value.type == ValueType.NULL:
            return "null"
        if value.type == ValueType.BOOLEAN:
            return "true" if value.value else "false"
        if value.type == ValueType.NUMBER:
            return str(int(value.value) if value.value.is_integer() else value.value)
        return str(value.value)

class BreakException(Exception):
    pass

def run(source: str):
    from .lexer import Scanner
    from .parser import Parser
    
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    
    parser = Parser(tokens)
    statements = parser.parse()
    
    interpreter = Interpreter()
    interpreter.interpret(statements)

def run_file(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        source = file.read()
    run(source)
