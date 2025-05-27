"""
NooCrush - A hybrid language combining Python, Rust, and JavaScript features.
"""

__version__ = "0.1.0"

from .lexer import Scanner, Token, TokenType
from .parser import Parser
from .interpreter import Interpreter, run

__all__ = ['Scanner', 'Token', 'TokenType', 'Parser', 'Interpreter', 'run']
