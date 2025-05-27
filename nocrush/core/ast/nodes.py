"""
Abstract Syntax Tree (AST) nodes for the NooCrush language.
"""
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any


@dataclass
class Node:
    """Base class for all AST nodes."""
    lineno: int
    col_offset: int
    
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        method_name = f'visit_{self.__class__.__name__}'
        visitor_method = getattr(visitor, method_name, None)
        if visitor_method is None:
            return visitor.generic_visit(self)
        return visitor_method(self)


@dataclass
class Module(Node):
    """Represents a module (a collection of statements)."""
    body: List['Stmt']
    type_ignores: List[Any] = None


@dataclass
class Expr(Node):
    """Base class for all expression nodes."""
    pass


@dataclass
class Stmt(Node):
    """Base class for all statement nodes."""
    pass


# Literal expressions
@dataclass
class Constant(Expr):
    """Represents a constant value (string, number, etc.)."""
    value: Union[str, int, float, bool, None]
    kind: Optional[str] = None


@dataclass
class Name(Expr):
    """Represents a variable name."""
    id: str
    ctx: 'expr_context'


# Variables
@dataclass
class NameConstant(Expr):
    """Represents constants like None, True, False."""
    value: Optional[bool]


@dataclass
class Num(Expr):
    """Represents a numeric literal."""
    n: Union[int, float]


@dataclass
class Str(Expr):
    """Represents a string literal."""
    s: str


# Operations
@dataclass
class UnaryOp(Expr):
    """Represents a unary operation (e.g., -x, not x)."""
    op: 'unaryop'
    operand: Expr


@dataclass
class BinOp(Expr):
    """Represents a binary operation (e.g., x + y)."""
    left: Expr
    op: 'operator'
    right: Expr


@dataclass
class BoolOp(Expr):
    """Represents a boolean operation (and/or)."""
    op: 'boolop'
    values: List[Expr]


@dataclass
class Compare(Expr):
    """Represents a comparison of two or more values."""
    left: Expr
    ops: List['cmpop']
    comparators: List[Expr]


# Control flow
@dataclass
class If(Stmt):
    """Represents an if statement."""
    test: Expr
    body: List[Stmt]
    orelse: List[Stmt]


@dataclass
class While(Stmt):
    """Represents a while loop."""
    test: Expr
    body: List[Stmt]
    orelse: List[Stmt] = None


@dataclass
class For(Stmt):
    """Represents a for loop."""
    target: Expr
    iter: Expr
    body: List[Stmt]
    orelse: List[Stmt] = None
    type_comment: str = None


@dataclass
class Break(Stmt):
    """Represents a break statement."""
    pass


@dataclass
class Continue(Stmt):
    """Represents a continue statement."""
    pass


@dataclass
class Return(Stmt):
    """Represents a return statement."""
    value: Optional[Expr] = None


# Function and class definitions
@dataclass
class FunctionDef(Stmt):
    """Represents a function definition."""
    name: str
    args: 'arguments'
    body: List[Stmt]
    decorator_list: List[Expr] = None
    returns: Expr = None
    type_comment: str = None


@dataclass
class ClassDef(Stmt):
    """Represents a class definition."""
    name: str
    bases: List[Expr]
    keywords: List['keyword']
    body: List[Stmt]
    decorator_list: List[Expr] = None


@dataclass
class AsyncFunctionDef(FunctionDef):
    """Represents an async function definition."""
    pass


# Imports
@dataclass
class Import(Stmt):
    """Represents an import statement."""
    names: List['alias']


@dataclass
class ImportFrom(Stmt):
    """Represents a from ... import statement."""
    module: Optional[str]
    names: List['alias']
    level: int = 0


# Other statements
@dataclass
class Assign(Stmt):
    """Represents an assignment."""
    targets: List[Expr]
    value: Expr
    type_comment: str = None


@dataclass
class AugAssign(Stmt):
    """Represents an augmented assignment (e.g., x += 1)."""
    target: Expr
    op: 'operator'
    value: Expr


@dataclass
class ExprStmt(Stmt):
    """Represents an expression as a statement."""
    value: Expr


# Contexts
@dataclass
class expr_context(Node):
    """Base class for expression contexts."""
    pass


@dataclass
class Load(expr_context):
    """Represents a load context (reading a value)."""
    pass


@dataclass
class Store(expr_context):
    """Represents a store context (assigning a value)."""
    pass


@dataclass
class Del(expr_context):
    """Represents a delete context (deleting a name)."""
    pass


# Other AST components
@dataclass
class arguments:
    """Represents arguments in a function definition."""
    posonlyargs: List['arg'] = None
    args: List['arg'] = None
    vararg: 'arg' = None
    kwonlyargs: List['arg'] = None
    kw_defaults: List[Optional[Expr]] = None
    kwarg: 'arg' = None
    defaults: List[Expr] = None


@dataclass
class arg:
    """Represents a single argument in a function definition."""
    arg: str
    annotation: Expr = None
    type_comment: str = None


@dataclass
class keyword:
    """Represents a keyword argument in a function call."""
    arg: Optional[str]
    value: Expr


@dataclass
class alias:
    """Represents an import alias."""
    name: str
    asname: Optional[str] = None


# Operator AST nodes
class operator(Node):
    """Base class for operators."""
    pass


class Add(operator):
    """Represents the + operator."""
    pass


class Sub(operator):
    """Represents the - operator."""
    pass


class Mult(operator):
    """Represents the * operator."""
    pass


class MatMult(operator):
    """Represents the @ operator (matrix multiplication)."""
    pass


class Div(operator):
    """Represents the / operator."""
    pass


class Mod(operator):
    """Represents the % operator."""
    pass


class Pow(operator):
    """Represents the ** operator."""
    pass


class LShift(operator):
    """Represents the << operator."""
    pass


class RShift(operator):
    """Represents the >> operator."""
    pass


class BitOr(operator):
    """Represents the | operator."""
    pass


class BitXor(operator):
    """Represents the ^ operator."""
    pass


class BitAnd(operator):
    """Represents the & operator."""
    pass


class FloorDiv(operator):
    """Represents the // operator."""
    pass


# Unary operators
class unaryop(Node):
    """Base class for unary operators."""
    pass


class UAdd(unaryop):
    """Represents the unary + operator."""
    pass


class USub(unaryop):
    """Represents the unary - operator."""
    pass


class Not(unaryop):
    """Represents the not operator."""
    pass


class Invert(unaryop):
    """Represents the ~ operator."""
    pass


# Boolean operators
class boolop(Node):
    """Base class for boolean operators."""
    pass


class And(boolop):
    """Represents the and operator."""
    pass


class Or(boolop):
    """Represents the or operator."""
    pass


# Comparison operators
class cmpop(Node):
    """Base class for comparison operators."""
    pass


class Eq(cmpop):
    """Represents the == operator."""
    pass


class NotEq(cmpop):
    """Represents the != operator."""
    pass


class Lt(cmpop):
    """Represents the < operator."""
    pass


class LtE(cmpop):
    """Represents the <= operator."""
    pass


class Gt(cmpop):
    """Represents the > operator."""
    pass


class GtE(cmpop):
    """Represents the >= operator."""
    pass


class Is(cmpop):
    """Represents the 'is' operator."""
    pass


class IsNot(cmpop):
    """Represents the 'is not' operator."""
    pass


class In(cmpop):
    """Represents the 'in' operator."""
    pass


class NotIn(cmpop):
    """Represents the 'not in' operator."""
    pass


# Type aliases for type hints
Stmt = Union[
    FunctionDef, ClassDef, Return, Delete, Assign, AugAssign, For, While, If, With, Raise,
    Try, Assert, Import, ImportFrom, Global, Nonlocal, ExprStmt, Pass, Break, Continue
]

Expr = Union[
    BoolOp, BinOp, UnaryOp, Lambda, IfExp, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp,
    Await, Yield, YieldFrom, Compare, Call, Num, Str, FormattedValue, JoinedStr, Bytes, NameConstant,
    Ellipsis, Constant, Attribute, Subscript, Starred, Name, List, Tuple
]

expr_context = Union[Load, Store, Del, AugLoad, AugStore, Param]
