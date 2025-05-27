"""
Tests for the NooCrush parser.
"""
import pytest
from noocrush.lexer import Scanner
from noocrush.parser import Parser
from noocrush.ast import (
    Program, VariableDeclaration, FunctionDeclaration, IfStatement,
    WhileStatement, ReturnStatement, ExpressionStatement, Binary, Unary, Literal, Variable, Call, Grouping,
    Assign, Logical, Get, Set, This, Super, ListLiteral, DictLiteral, Subscript, Slice, ListComprehension
)

def parse_source(source):
    """Helper function to parse source code and return the AST."""
    scanner = Scanner()
    scanner.source = source
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()

def test_variable_declaration():
    """Test parsing variable declarations."""
    source = """
    let x = 42;
    const name = "NooCrush";
    """
    statements = parse_source(source)
    
    assert len(statements) == 2
    
    # Check first declaration (let x = 42;)
    assert isinstance(statements[0], VariableDeclaration)
    assert statements[0].name.lexeme == "x"
    assert statements[0].mutable is True
    assert isinstance(statements[0].initializer, Literal)
    assert statements[0].initializer.value == 42
    
    # Check second declaration (const name = "NooCrush";)
    assert isinstance(statements[1], VariableDeclaration)
    assert statements[1].name.lexeme == "name"
    assert statements[1].mutable is False
    assert isinstance(statements[1].initializer, Literal)
    assert statements[1].initializer.value == "NooCrush"

def test_function_declaration():
    """Test parsing function declarations."""
    source = """
    fn add(a: Number, b: Number) -> Number {
        return a + b;
    }
    """
    statements = parse_source(source)
    
    assert len(statements) == 1
    assert isinstance(statements[0], FunctionDeclaration)
    assert statements[0].name.lexeme == "add"
    
    # Check parameters
    assert len(statements[0].params) == 2
    assert statements[0].params[0]["name"] == "a"
    assert statements[0].params[0]["type"] == "Number"
    assert statements[0].params[1]["name"] == "b"
    assert statements[0].params[1]["type"] == "Number"
    
    # Check return type
    assert statements[0].return_type == "Number"
    
    # Check body
    assert len(statements[0].body) == 1
    assert isinstance(statements[0].body[0], ReturnStatement)
    assert isinstance(statements[0].body[0].value, Binary)

def test_if_statement():
    """Test parsing if statements."""
    source = """
    if (x > 0) {
        print("Positive");
    } else if (x < 0) {
        print("Negative");
    } else {
        print("Zero");
    }
    """
    statements = parse_source(source)
    
    assert len(statements) == 1
    assert isinstance(statements[0], IfStatement)
    
    # Check condition
    assert isinstance(statements[0].condition, Binary)
    
    # Check then branch
    assert len(statements[0].then_branch) == 1
    assert isinstance(statements[0].then_branch[0], ExpressionStatement)
    
    # Check else if branch
    assert isinstance(statements[0].else_branch, IfStatement)
    
    # Check else branch
    assert len(statements[0].else_branch.else_branch) == 1
    assert isinstance(statements[0].else_branch.else_branch[0], ExpressionStatement)

def test_while_loop():
    """Test parsing while loops."""
    source = """
    while (i < 10) {
        print(i);
        i = i + 1;
    }
    """
    statements = parse_source(source)
    
    assert len(statements) == 1
    assert isinstance(statements[0], WhileStatement)
    
    # Check condition
    assert isinstance(statements[0].condition, Binary)
    
    # Check body
    assert len(statements[0].body) == 2
    assert isinstance(statements[0].body[0], ExpressionStatement)
    assert isinstance(statements[0].body[1], ExpressionStatement)

def test_binary_expressions():
    """Test parsing binary expressions with proper operator precedence."""
    source = "1 + 2 * 3 == 7 && true || false"
    statements = parse_source(source)
    
    # Should be a single expression statement
    assert len(statements) == 1
    assert isinstance(statements[0], ExpressionStatement)
    
    # Check operator precedence: 1 + (2 * 3) == 7 && true || false
    expr = statements[0].expression
    assert isinstance(expr, Logical)
    assert expr.operator.type == "OR"
    
    # Left side of OR: (1 + (2 * 3) == 7) && true
    left = expr.left
    assert isinstance(left, Logical)
    assert left.operator.type == "AND"
    
    # Right side of OR: false
    assert isinstance(expr.right, Literal)
    assert expr.right.value is False

def test_list_operations():
    """Test parsing list operations."""
    source = """
    let numbers = [1, 2, 3];
    let first = numbers[0];
    let slice = numbers[1:3];
    """
    statements = parse_source(source)
    
    assert len(statements) == 3
    
    # Check list literal
    assert isinstance(statements[0], VariableDeclaration)
    assert isinstance(statements[0].initializer, ListLiteral)
    assert len(statements[0].initializer.elements) == 3
    
    # Check list indexing
    assert isinstance(statements[1], VariableDeclaration)
    assert isinstance(statements[1].initializer, Subscript)
    
    # Check list slicing
    assert isinstance(statements[2], VariableDeclaration)
    assert isinstance(statements[2].initializer, Subscript)
    assert isinstance(statements[2].initializer.slice, Slice)

def test_list_comprehension():
    """Test parsing list comprehensions."""
    source = "[x * 2 for x in numbers if x > 0]"
    statements = parse_source(source)
    
    assert len(statements) == 1
    assert isinstance(statements[0], ExpressionStatement)
    assert isinstance(statements[0].expression, ListComprehension)
    
    lc = statements[0].expression
    assert isinstance(lc.expression, Binary)
    assert isinstance(lc.item, Variable)
    assert lc.item.name.lexeme == "x"
    assert isinstance(lc.iterable, Variable)
    assert lc.iterable.name.lexeme == "numbers"
    assert isinstance(lc.condition, Binary)

def test_dict_literal():
    """Test parsing dictionary literals."""
    source = """
    let person = {
        "name": "Alice",
        "age": 30,
        "active": true
    };
    """
    statements = parse_source(source)
    
    assert len(statements) == 1
    assert isinstance(statements[0], VariableDeclaration)
    assert isinstance(statements[0].initializer, DictLiteral)
    
    # Check dictionary entries
    entries = statements[0].initializer.entries
    assert len(entries) == 3
    
    # Check first entry ("name": "Alice")
    assert isinstance(entries[0]["key"], Literal)
    assert entries[0]["key"].value == "name"
    assert isinstance(entries[0]["value"], Literal)
    assert entries[0]["value"].value == "Alice"
    
    # Check second entry ("age": 30)
    assert entries[1]["key"].value == "age"
    assert entries[1]["value"].value == 30
    
    # Check third entry ("active": true)
    assert entries[2]["key"].value == "active"
    assert entries[2]["value"].value is True

# Add more test cases for error handling, edge cases, etc.
