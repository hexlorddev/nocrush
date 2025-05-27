""
Lexical analyzer (tokenizer) for the NooCrush language.
"""
from enum import Enum, auto
from typing import List, Dict, Any, Optional

class TokenType(Enum):
    # Single-character tokens
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    BACKTICK = auto()
    COLON = auto()
    
    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    
    # Keywords
    AND = auto()
    ASYNC = auto()
    AWAIT = auto()
    BREAK = auto()
    CONST = auto()
    ELSE = auto()
    FALSE = auto()
    FN = auto()
    FOR = auto()
    IF = auto()
    IN = auto()
    LET = auto()
    LOOP = auto()
    MUT = auto()
    RETURN = auto()
    STRUCT = auto()
    TRUE = auto()
    
    # Types
    NUMBER_TYPE = auto()
    STRING_TYPE = auto()
    BOOL_TYPE = auto()
    
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: Any, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"

class Scanner:
    keywords = {
        'and': TokenType.AND,
        'async': TokenType.ASYNC,
        'await': TokenType.AWAIT,
        'break': TokenType.BREAK,
        'const': TokenType.CONST,
        'else': TokenType.ELSE,
        'false': TokenType.FALSE,
        'fn': TokenType.FN,
        'for': TokenType.FOR,
        'if': TokenType.IF,
        'in': TokenType.IN,
        'let': TokenType.LET,
        'loop': TokenType.LOOP,
        'mut': TokenType.MUT,
        'return': TokenType.RETURN,
        'struct': TokenType.STRUCT,
        'true': TokenType.TRUE,
        'Number': TokenType.NUMBER_TYPE,
        'String': TokenType.STRING_TYPE,
        'Bool': TokenType.BOOL_TYPE,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
    
    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def scan_token(self):
        c = self.advance()
        
        if c == '(': self.add_token(TokenType.LEFT_PAREN)
        elif c == ')': self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{': self.add_token(TokenType.LEFT_BRACE)
        elif c == '}': self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',': self.add_token(TokenType.COMMA)
        elif c == '.': self.add_token(TokenType.DOT)
        elif c == '-': self.add_token(TokenType.MINUS)
        elif c == '+': self.add_token(TokenType.PLUS)
        elif c == ';': self.add_token(TokenType.SEMICOLON)
        elif c == '*': self.add_token(TokenType.STAR)
        elif c == '`': self.add_token(TokenType.BACKTICK)
        elif c == ':': self.add_token(TokenType.COLON)
        
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        
        elif c == '/':
            if self.match('/'):
                # A comment goes until the end of the line
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                # Block comment
                while not (self.peek() == '*' and self.peek_next() == '/') and not self.is_at_end():
                    if self.peek() == '\n':
                        self.line += 1
                    self.advance()
                
                # Consume the closing '*'
                if not self.is_at_end():
                    self.advance()  # '*'
                    self.advance()  # '/'
            else:
                self.add_token(TokenType.SLASH)
        
        elif c in [' ', '\r', '\t']:
            # Ignore whitespace
            pass
        elif c == '\n':
            self.line += 1
        
        elif c == '"':
            self.string()
        
        else:
            if c.isdigit():
                self.number()
            elif c.isalpha() or c == '_':
                self.identifier()
            else:
                print(f"Unexpected character: {c}")
    
    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)
    
    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        # Look for a fractional part
        if self.peek() == '.' and self.peek_next().isdigit():
            # Consume the "."
            self.advance()
            
            while self.peek().isdigit():
                self.advance()
        
        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))
    
    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            print("Unterminated string.")
            return
        
        # The closing "
        self.advance()
        
        # Trim the surrounding quotes
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True
    
    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]
    
    def add_token(self, type: TokenType, literal: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
