#!/usr/bin/env python3

import sys
import re
from typing import List, Tuple, Optional, Dict, Any

class Token:
    def __init__(self, type: str, value: Any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})'

class NooCrushLexer:
    def __init__(self):
        self.keywords = {
            'let': 'LET',
            'const': 'CONST',
            'fn': 'FN',
            'mut': 'MUT',
            'async': 'ASYNC',
            'await': 'AWAIT',
            'if': 'IF',
            'else': 'ELSE',
            'loop': 'LOOP',
            'break': 'BREAK',
            'return': 'RETURN',
            'struct': 'STRUCT'
        }
        
        self.tokens: List[Token] = []
        self.source = ''
        self.pos = 0
        self.line = 1
        self.column = 1

    def error(self, message: str) -> None:
        raise SyntaxError(f'Line {self.line}, Column {self.column}: {message}')

    def advance(self) -> None:
        self.pos += 1
        self.column += 1

    def newline(self) -> None:
        self.line += 1
        self.column = 1

    def peek(self) -> Optional[str]:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def tokenize(self, source: str) -> List[Token]:
        self.source = source
        self.tokens = []
        self.pos = 0
        self.line = 1
        self.column = 1

        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            # Handle whitespace
            if char.isspace():
                if char == '\n':
                    self.newline()
                self.advance()
                continue

            # Handle comments
            if char == '/' and self.peek() == '/':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.advance()
                continue

            # Handle identifiers and keywords
            if char.isalpha() or char == '_':
                start_col = self.column
                identifier = self.consume_while(lambda c: c.isalnum() or c == '_')
                token_type = self.keywords.get(identifier, 'IDENTIFIER')
                self.tokens.append(Token(token_type, identifier, self.line, start_col))
                continue

            # Handle numbers
            if char.isdigit():
                start_col = self.column
                number = self.consume_while(lambda c: c.isdigit() or c == '.')
                try:
                    value = float(number) if '.' in number else int(number)
                    self.tokens.append(Token('NUMBER', value, self.line, start_col))
                except ValueError:
                    self.error(f'Invalid number format: {number}')
                continue

            # Handle strings
            if char in '\"\'':
                self.tokenize_string(char)
                continue

            # Handle operators
            if char in '+-*/%=<>!&|^':
                start_col = self.column
                operator = self.consume_while(lambda c: c in '+-*/%=<>!&|^')
                self.tokens.append(Token('OPERATOR', operator, self.line, start_col))
                continue

            # Handle delimiters
            if char in '(){}[],:;':
                self.tokens.append(Token('DELIMITER', char, self.line, self.column))
                self.advance()
                continue

            self.error(f'Unexpected character: {char}')

        # Add EOF token
        self.tokens.append(Token('EOF', None, self.line, self.column))
        return self.tokens

    def consume_while(self, predicate) -> str:
        result = ''
        while self.pos < len(self.source) and predicate(self.source[self.pos]):
            result += self.source[self.pos]
            self.advance()
        return result

    def tokenize_string(self, quote: str) -> None:
        start_col = self.column
        self.advance()  # Skip opening quote
        string = ''
        
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            if char == '\n':
                self.error('Unterminated string literal')
            
            if char == quote:
                self.advance()  # Skip closing quote
                self.tokens.append(Token('STRING', string, self.line, start_col))
                return
            
            if char == '\\':
                self.advance()
                if self.pos >= len(self.source):
                    self.error('Unterminated string literal')
                char = self.source[self.pos]
                if char in {'n', 't', 'r', '\\', quote}:
                    string += {'n': '\n', 't': '\t', 'r': '\r'}.get(char, char)
                else:
                    self.error(f'Invalid escape sequence: \\{char}')
            else:
                string += char
            self.advance()
        
        self.error('Unterminated string literal')

class NooCrushParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Dict[str, Any]:
        # TODO: Implement full parser
        return {'type': 'Program', 'body': self.tokens}

def main():
    if len(sys.argv) != 2:
        print('Usage: python noocrush.py <source_file>')
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f'Error: Could not find file {sys.argv[1]}')
        sys.exit(1)
    except Exception as e:
        print(f'Error reading file: {e}')
        sys.exit(1)

    try:
        lexer = NooCrushLexer()
        tokens = lexer.tokenize(source)
        parser = NooCrushParser(tokens)
        ast = parser.parse()
        
        print('=== Tokens ===')
        for token in tokens:
            print(token)
        
        print('\n=== Abstract Syntax Tree ===')
        print(ast)
        
    except SyntaxError as e:
        print(f'Syntax Error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Unexpected error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()