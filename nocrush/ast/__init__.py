"""
Abstract Syntax Tree (AST) definitions for NooCrush language.
"""
from dataclasses import dataclass
from typing import List, Optional, Any, Dict, Union

# Base class for all AST nodes
@dataclass
class Node:
    """Base class for all AST nodes."""
    pass

# Expressions
@dataclass
class Expr(Node):
    """Base class for all expression nodes."""
    pass

@dataclass
class Literal(Expr):
    """Literal value expression (e.g., 42, "hello", true)."""
    value: Any
    value_type: str

@dataclass
class Variable(Expr):
    """Variable reference expression."""
    name: str

@dataclass
class Binary(Expr):
    """Binary operation expression."""
    left: Expr
    operator: Any  # Token
    right: Expr

@dataclass
class Unary(Expr):
    """Unary operation expression."""
    operator: Any  # Token
    right: Expr

@dataclass
class Call(Expr):
    """Function call expression."""
    callee: Expr
    arguments: List[Expr]
    paren: Any  # Token

# Statements
@dataclass
class Stmt(Node):
    """Base class for all statement nodes."""
    pass

@dataclass
class Expression(Stmt):
    """Expression statement."""
    expression: Expr

@dataclass
class Var(Stmt):
    """Variable declaration statement."""
    name: str
    initializer: Optional[Expr]
    var_type: Optional[str] = None
    is_const: bool = False

@dataclass
class Block(Stmt):
    """Block of statements."""
    statements: List[Stmt]

@dataclass
class If(Stmt):
    """If statement."""
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt] = None

@dataclass
class Loop(Stmt):
    """Loop statement."""
    body: Stmt

@dataclass
class Function(Stmt):
    """Function declaration."""
    name: str
    parameters: List[Dict[str, str]]  # List of {'name': str, 'type': str}
    body: List[Stmt]
    return_type: Optional[str] = None

@dataclass
class Return(Stmt):
    """Return statement."""
    keyword: Any  # Token
    value: Optional[Expr] = None

@dataclass
class Struct(Stmt):
    """Struct declaration."""
    name: str
    fields: List[Dict[str, Any]]  # List of {'name': str, 'type': str, 'mutable': bool}
