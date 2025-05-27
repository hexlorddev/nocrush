"""
Token definitions for the NooCrush lexer.
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Tuple, Any


class TokenType(Enum):
    """Enumeration of all token types in NooCrush."""
    # Single-character tokens
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COMMA = ","
    DOT = "."
    COLON = ":"
    SEMICOLON = ";"
    QUESTION = "?"
    AT = "@"
    BACKTICK = "`"
    
    # One or two character tokens
    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    PLUS = "+"
    PLUS_EQUAL = "+="
    MINUS = "-"
    MINUS_EQUAL = "-="
    STAR = "*"
    STAR_EQUAL = "*="
    STAR_STAR = "**"
    SLASH = "/"
    SLASH_EQUAL = "/="
    PERCENT = "%"
    PERCENT_EQUAL = "%="
    AMPERSAND = "&"
    PIPE = "|"
    CARET = "^"
    TILDE = "~"
    LEFT_SHIFT = "<<"
    RIGHT_SHIFT = ">>"
    
    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    
    # Keywords
    AND = "and"
    AS = "as"
    ASSERT = "assert"
    ASYNC = "async"
    AWAIT = "await"
    BREAK = "break"
    CLASS = "class"
    CONTINUE = "continue"
    DEF = "def"
    DEL = "del"
    ELIF = "elif"
    ELSE = "else"
    EXCEPT = "except"
    FALSE = "False"
    FINALLY = "finally"
    FOR = "for"
    FROM = "from"
    GLOBAL = "global"
    IF = "if"
    IMPORT = "import"
    IN = "in"
    IS = "is"
    LAMBDA = "lambda"
    NONE = "None"
    NONLOCAL = "nonlocal"
    NOT = "not"
    OR = "or"
    PASS = "pass"
    RAISE = "raise"
    RETURN = "return"
    SELF = "self"
    SUPER = "super"
    TRUE = "True"
    TRY = "try"
    WHILE = "while"
    WITH = "with"
    YIELD = "yield"
    
    # Type hints
    ANNOTATION = "->"
    
    # Special tokens
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    ENDMARKER = "ENDMARKER"
    
    # Error token
    ERROR = "ERROR"


@dataclass
class Token:
    """Represents a token in the source code."""
    type: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int
    filename: str = "<string>"
    
    def __str__(self) -> str:
        """Return a string representation of the token."""
        return f"{self.type.name} {self.lexeme} {self.literal}"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the token."""
        return (f"Token(type={self.type}, lexeme='{self.lexeme}', "
                f"literal={self.literal}, line={self.line}, column={self.column})")


# Keywords mapping
KEYWORDS = {
    'and': TokenType.AND,
    'as': TokenType.AS,
    'assert': TokenType.ASSERT,
    'async': TokenType.ASYNC,
    'await': TokenType.AWAIT,
    'break': TokenType.BREAK,
    'class': TokenType.CLASS,
    'continue': TokenType.CONTINUE,
    'def': TokenType.DEF,
    'del': TokenType.DEL,
    'elif': TokenType.ELIF,
    'else': TokenType.ELSE,
    'except': TokenType.EXCEPT,
    'False': TokenType.FALSE,
    'finally': TokenType.FINALLY,
    'for': TokenType.FOR,
    'from': TokenType.FROM,
    'global': TokenType.GLOBAL,
    'if': TokenType.IF,
    'import': TokenType.IMPORT,
    'in': TokenType.IN,
    'is': TokenType.IS,
    'lambda': TokenType.LAMBDA,
    'None': TokenType.NONE,
    'nonlocal': TokenType.NONLOCAL,
    'not': TokenType.NOT,
    'or': TokenType.OR,
    'pass': TokenType.PASS,
    'raise': TokenType.RAISE,
    'return': TokenType.RETURN,
    'self': TokenType.SELF,
    'super': TokenType.SUPER,
    'True': TokenType.TRUE,
    'try': TokenType.TRY,
    'while': TokenType.WHILE,
    'with': TokenType.WITH,
    'yield': TokenType.YIELD,
}

# Single-character tokens
SINGLE_CHAR_TOKENS = {
    '(': TokenType.LEFT_PAREN,
    ')': TokenType.RIGHT_PAREN,
    '{': TokenType.LEFT_BRACE,
    '}': TokenType.RIGHT_BRACE,
    '[': TokenType.LEFT_BRACKET,
    ']': TokenType.RIGHT_BRACKET,
    ',': TokenType.COMMA,
    '.': TokenType.DOT,
    ':': TokenType.COLON,
    ';': TokenType.SEMICOLON,
    '?': TokenType.QUESTION,
    '@': TokenType.AT,
    '`': TokenType.BACKTICK,
    '~': TokenType.TILDE,
}

# Multi-character tokens (first character)
MULTI_CHAR_STARTS = {
    '!': [('!=', TokenType.BANG_EQUAL)],
    '=': [('==', TokenType.EQUAL_EQUAL)],
    '<': [('<=', TokenType.LESS_EQUAL), ('<<', TokenType.LEFT_SHIFT)],
    '>': [('>=', TokenType.GREATER_EQUAL), ('>>', TokenType.RIGHT_SHIFT)],
    '+': [('+=', TokenType.PLUS_EQUAL)],
    '-': [('-=', TokenType.MINUS_EQUAL), ('->', TokenType.ANNOTATION)],
    '*': [('*=', TokenType.STAR_EQUAL), ('**', TokenType.STAR_STAR)],
    '/': [('/=', TokenType.SLASH_EQUAL)],
    '%': ['%=', TokenType.PERCENT_EQUAL],
    '&': [('&', TokenType.AMPERSAND)],
    '|': [('|', TokenType.PIPE)],
    '^': [('^', TokenType.CARET)],
}

# All operators for operator precedence
OPERATORS = {
    # Precedence level 1 (highest)
    '**': 1,
    '~': 1,
    '+@': 1,  # Unary plus
    '-@': 1,  # Unary minus
    
    # Precedence level 2
    '*': 2,
    '@': 2,  # Matrix multiplication
    '/': 2,
    '//': 2,
    '%': 2,
    
    # Precedence level 3
    '+': 3,
    '-': 3,
    
    # Precedence level 4
    '<<': 4,
    '>>': 4,
    
    # Precedence level 5
    '&': 5,
    
    # Precedence level 6
    '^': 6,
    
    # Precedence level 7
    '|': 7,
    
    # Precedence level 8 (comparisons, in, is, is not, not in, <, <=, >, >=, !=, ==)
    'in': 8,
    'not in': 8,
    'is': 8,
    'is not': 8,
    '<': 8,
    '<=': 8,
    '>': 8,
    '>=': 8,
    '==': 8,
    '!=': 8,
    
    # Precedence level 9 (logical NOT)
    'not': 9,
    
    # Precedence level 10 (logical AND)
    'and': 10,
    
    # Precedence level 11 (logical OR)
    'or': 11,
}

# Assignment operators
ASSIGNMENT_OPS = {
    '=', '+=', '-=', '*=', '/=', '%=', '**=', '//=', '@=',
    '&=', '|=', '^=', '<<=', '>>=', '**=',
}

# Augmented assignment operators
AUGMENTED_ASSIGNMENT_OPS = {
    '+=', '-=', '*=', '/=', '%=', '**=', '//=', '@=',
    '&=', '|=', '^=', '<<=', '>>=', '**=',
}

# Comparison operators
COMPARISON_OPS = {
    '==', '!=', '<', '<=', '>', '>=', 'in', 'not in', 'is', 'is not'
}

# Binary operators
BINARY_OPS = {
    '+', '-', '*', '**', '/', '//', '%', '<<', '>>', '&', '|', '^', '~',
    'and', 'or', 'is', 'is not', 'in', 'not in',
}

# Unary operators
UNARY_OPS = {'+', '-', '~', 'not'}

# All keywords that start a statement
STATEMENT_KEYWORDS = {
    'if', 'for', 'while', 'try', 'with', 'def', 'class', 'async',
    'return', 'yield', 'raise', 'break', 'continue', 'import', 'from',
    'global', 'nonlocal', 'assert', 'pass', 'del',
}

# All keywords that start an expression
EXPRESSION_KEYWORDS = {
    'True', 'False', 'None', 'lambda', 'await',
}

# All reserved keywords
RESERVED_KEYWORDS = set(KEYWORDS.keys())

# String quotes
STRING_QUOTES = {"'", '"', "'''", '"""'}

# Whitespace characters
WHITESPACE = {' ', '\t', '\f'}

# Newline characters
NEWLINE = {'\n', '\r', '\r\n'}

# Indentation characters
INDENT = '    '  # 4 spaces

# Maximum indentation level
MAX_INDENT_LEVEL = 100

# Maximum string length
MAX_STRING_LENGTH = 4 * 1024 * 1024  # 4MB

# Maximum number of nested parentheses/brackets/braces
MAX_NESTING_LEVEL = 100

# Maximum number of tokens in a single line
MAX_TOKENS_PER_LINE = 1000

# Maximum line length
MAX_LINE_LENGTH = 1000

# Maximum number of errors before giving up
MAX_ERRORS = 100

# Token types that can start an expression
EXPRESSION_STARTERS = {
    TokenType.LEFT_PAREN, TokenType.LEFT_BRACKET, TokenType.LEFT_BRACE,
    TokenType.NAME, TokenType.NUMBER, TokenType.STRING,
    TokenType.TRUE, TokenType.FALSE, TokenType.NONE,
    TokenType.NOT, TokenType.MINUS, TokenType.PLUS, TokenType.TILDE,
    TokenType.STAR, TokenType.STAR_STAR,
}

# Token types that can be used in a type annotation
TYPE_ANNOTATION_TOKENS = {
    TokenType.NAME, TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET,
    TokenType.COMMA, TokenType.ELLIPSIS, TokenType.COLON,
    TokenType.OR, TokenType.PIPE,  # For Union types (X | Y)
}

# Token types that can appear in a decorator
DECORATOR_TOKENS = {
    TokenType.NAME, TokenType.DOT, TokenType.LEFT_PAREN,
    TokenType.RIGHT_PAREN, TokenType.COMMA, TokenType.EQUAL,
    TokenType.STRING, TokenType.NUMBER, TokenType.TRUE, TokenType.FALSE,
    TokenType.NONE, TokenType.ELLIPSIS,
}

# Token types that can appear in a slice
SLICE_TOKENS = {
    TokenType.COLON, TokenType.NUMBER, TokenType.NAME,
    TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN,
    TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
    TokenType.PERCENT, TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET,
    TokenType.COMMA,
}
