"""
Lexical analyzer for the NooCrush programming language.
"""
import re
from typing import List, Dict, Tuple, Optional, Pattern, Callable, Any
from dataclasses import dataclass
from enum import Enum, auto

from noocrush.core.lexer.tokens import (
    Token, TokenType, KEYWORDS, SINGLE_CHAR_TOKENS, MULTI_CHAR_STARTS,
    STRING_QUOTES, WHITESPACE, NEWLINE, INDENT, MAX_INDENT_LEVEL,
    MAX_STRING_LENGTH, MAX_NESTING_LEVEL, MAX_TOKENS_PER_LINE, MAX_LINE_LENGTH,
    MAX_ERRORS, EXPRESSION_STARTERS, TYPE_ANNOTATION_TOKENS, DECORATOR_TOKENS,
    SLICE_TOKENS, OPERATORS, ASSIGNMENT_OPS, AUGMENTED_ASSIGNMENT_OPS,
    COMPARISON_OPS, BINARY_OPS, UNARY_OPS, STATEMENT_KEYWORDS, EXPRESSION_KEYWORDS,
    RESERVED_KEYWORDS
)


class LexerError(Exception):
    """Base class for lexer errors."""
    pass


class LexerSyntaxError(LexerError):
    """Raised when a syntax error is encountered during lexing."""
    def __init__(self, message: str, line: int, column: int, filename: str = "<string>"):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column}: {self.message}"


class LexerWarning(Warning):
    """Base class for lexer warnings."""
    pass


class IndentationWarning(LexerWarning):
    """Raised for inconsistent indentation."""
    pass


class LexerState(Enum):
    """Lexer state machine states."""
    START = auto()
    IN_IDENTIFIER = auto()
    IN_NUMBER = auto()
    IN_STRING = auto()
    IN_STRING_ESCAPE = auto()
    IN_COMMENT = auto()
    IN_FSTRING = auto()
    IN_FSTRING_EXPR = auto()
    IN_FSTRING_FORMAT_SPEC = auto()


class LexerMode(Enum):
    """Lexer operating modes."""
    NORMAL = auto()
    FORMAT_STRING = auto()
    TYPE_ANNOTATION = auto()
    DECORATOR = auto()
    SLICE = auto()


@dataclass
class LexerContext:
    """Context for the lexer state."""
    state: LexerState = LexerState.START
    mode: LexerMode = LexerMode.NORMAL
    indentation_stack: List[int] = None
    pending_dedents: int = 0
    paren_level: int = 0
    bracket_level: int = 0
    brace_level: int = 0
    fstring_stack: List[bool] = None
    format_spec_count: int = 0
    line_continuation: bool = False
    encoding: str = "utf-8"
    newline: str = "\n"
    
    def __post_init__(self):
        if self.indentation_stack is None:
            self.indentation_stack = [0]
        if self.fstring_stack is None:
            self.fstring_stack = []
    
    def enter_mode(self, mode: LexerMode) -> None:
        """Enter a new lexer mode."""
        self.mode = mode
    
    def exit_mode(self) -> LexerMode:
        """Exit the current lexer mode and return to the previous one."""
        self.mode = LexerMode.NORMAL
        return self.mode


class Lexer:
    """
    Lexical analyzer for the NooCrush programming language.
    
    The lexer converts source code into a sequence of tokens that can be
    parsed by the parser. It handles:
    - Whitespace and comments
    - Identifiers and keywords
    - Numeric literals (integers, floats, complex)
    - String literals (including f-strings and raw strings)
    - Operators and delimiters
    - Indentation and dedentation
    """
    
    def __init__(self, source: str, filename: str = "<string>"):
        """
        Initialize the lexer with source code.
        
        Args:
            source: The source code to lex.
            filename: The name of the source file (for error messages).
        """
        self.source = source
        self.filename = filename
        self.tokens: List[Token] = []
        self.errors: List[LexerError] = []
        self.warnings: List[LexerWarning] = []
        
        # Position tracking
        self.pos = 0
        self.line = 1
        self.column = 1
        self.start_pos = 0
        self.start_line = 1
        self.start_column = 1
        
        # State tracking
        self.context = LexerContext()
        
        # Regular expressions for token matching
        self._setup_patterns()
    
    def _setup_patterns(self) -> None:
        """Compile regular expressions for token matching."""
        # Identifier pattern (Python-style)
        self.identifier_pattern = re.compile(
            r'[A-Za-z_][A-Za-z0-9_]*',
            re.UNICODE
        )
        
        # Numeric patterns
        self.integer_pattern = re.compile(
            r'(?P<decimal>\d+|0[bB][01_]+|0[oO]?[0-7_]+|0[xX][0-9a-fA-F_]+)'
            r'(?P<exponent>[eE][+-]?\d+)?[jJ]?|\d+[jJ]',
            re.UNICODE
        )
        
        self.float_pattern = re.compile(
            r'\d+\.\d*(?:[eE][+-]?\d*)?[jJ]?|\d+(?:\.\d*)?[eE][+-]?\d+[jJ]?',
            re.UNICODE
        )
        
        # String patterns
        self.string_prefix_pattern = re.compile(
            r'[rRuUfF]*(?:"[^"]*"|\'[^\']*\')',
            re.UNICODE
        )
        
        # Whitespace pattern
        self.whitespace_pattern = re.compile(r'[ \t\f]+', re.UNICODE)
        
        # Newline pattern (handles \n, \r, \r\n)
        self.newline_pattern = re.compile(r'\r\n|\n|\r', re.UNICODE)
        
        # Comment pattern
        self.comment_pattern = re.compile(r'#[^\n\r]*', re.UNICODE)
    
    def tokenize(self) -> List[Token]:
        """
        Tokenize the source code.
        
        Returns:
            List of tokens.
        """
        try:
            while not self._is_at_end():
                self.start_pos = self.pos
                self.start_line = self.line
                self.start_column = self.column
                
                # Handle the current character based on lexer state
                if self.context.state == LexerState.START:
                    self._handle_start()
                elif self.context.state == LexerState.IN_IDENTIFIER:
                    self._handle_identifier()
                elif self.context.state == LexerState.IN_NUMBER:
                    self._handle_number()
                elif self.context.state == LexerState.IN_STRING:
                    self._handle_string()
                elif self.context.state == LexerState.IN_STRING_ESCAPE:
                    self._handle_string_escape()
                elif self.context.state == LexerState.IN_COMMENT:
                    self._handle_comment()
                elif self.context.state == LexerState.IN_FSTRING:
                    self._handle_fstring()
                elif self.context.state == LexerState.IN_FSTRING_EXPR:
                    self._handle_fstring_expr()
                elif self.context.state == LexerState.IN_FSTRING_FORMAT_SPEC:
                    self._handle_fstring_format_spec()
                else:
                    self._error(f"Unexpected lexer state: {self.context.state}")
            
            # Add end-of-file token
            self._add_token(TokenType.ENDMARKER, "")
            
            return self.tokens
            
        except LexerError as e:
            self.errors.append(e)
            raise
    
    def _handle_start(self) -> None:
        """Handle the start state of the lexer."""
        # Skip whitespace (except newlines which are significant)
        if self._match_pattern(self.whitespace_pattern):
            self._advance(len(self._current_match.group(0)))
            return
        
        # Handle newlines and indentation
        if self._match_pattern(self.newline_pattern):
            self._handle_newline()
            return
        
        # Handle comments
        if self._match_pattern(self.comment_pattern):
            self._handle_comment()
            return
        
        # Handle string literals
        if self._current_char() in STRING_QUOTES:
            self._handle_string_start()
            return
        
        # Handle numeric literals
        if self._current_char().isdigit() or (self._current_char() == '.' and self._peek().isdigit()):
            self.context.state = LexerState.IN_NUMBER
            return
        
        # Handle identifiers and keywords
        if self._current_char().isalpha() or self._current_char() == '_':
            self.context.state = LexerState.IN_IDENTIFIER
            return
        
        # Handle operators and delimiters
        self._handle_operator_or_delimiter()
    
    def _handle_identifier(self) -> None:
        """Handle identifiers and keywords."""
        if not (self._current_char().isalnum() or self._current_char() == '_'):
            # End of identifier
            lexeme = self.source[self.start_pos:self.pos]
            token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
            self._add_token(token_type, lexeme)
            self.context.state = LexerState.START
            return
        
        self._advance()
    
    def _handle_number(self) -> None:
        """Handle numeric literals."""
        # Simplified number handling - in a real implementation, this would be more complex
        while self._current_char().isdigit() or self._current_char() in '._':
            self._advance()
        
        # Handle decimal point
        if self._current_char() == '.':
            self._advance()
            while self._current_char().isdigit() or self._current_char() == '_':
                self._advance()
        
        # Handle exponent
        if self._current_char().lower() == 'e':
            self._advance()
            if self._current_char() in '+-':
                self._advance()
            while self._current_char().isdigit() or self._current_char() == '_':
                self._advance()
        
        # Handle complex numbers
        if self._current_char().lower() == 'j':
            self._advance()
        
        lexeme = self.source[self.start_pos:self.pos]
        self._add_token(TokenType.NUMBER, lexeme, float(lexeme.replace('_', '')))
        self.context.state = LexerState.START
    
    def _handle_string_start(self) -> None:
        """Handle the start of a string literal."""
        quote = self._current_char()
        self._advance()  # Consume the opening quote
        
        # Determine string type (normal, raw, f-string, etc.)
        is_raw = False
        is_fstring = False
        
        # In a real implementation, we would parse string prefixes here
        
        if is_fstring:
            self.context.state = LexerState.IN_FSTRING
            self.context.fstring_stack.append(True)
        else:
            self.context.state = LexerState.IN_STRING
        
        # Store string context for error reporting
        self._string_quote = quote
        self._string_prefix = 'f' if is_fstring else 'r' if is_raw else ''
    
    def _handle_string(self) -> None:
        """Handle string literals."""
        if self._current_char() == '\\':
            self.context.state = LexerState.IN_STRING_ESCAPE
            self._advance()
            return
        
        if self._current_char() == self._string_quote:
            # End of string
            self._advance()  # Consume the closing quote
            lexeme = self.source[self.start_pos:self.pos]
            # Remove quotes and handle escape sequences
            content = lexeme[len(self._string_prefix):-1]
            self._add_token(TokenType.STRING, lexeme, content)
            self.context.state = LexerState.START
            return
        
        if self._current_char() == '\n' and len(self._string_quote) == 1:
            self._error("Unterminated string literal")
        
        self._advance()
    
    def _handle_string_escape(self) -> None:
        """Handle escape sequences in strings."""
        # In a real implementation, this would handle all escape sequences
        self._advance()  # Skip the backslash
        self.context.state = LexerState.IN_STRING
    
    def _handle_comment(self) -> None:
        """Handle comments."""
        # Skip until end of line
        while self._current_char() not in ('\n', '\r') and not self._is_at_end():
            self._advance()
        
        # The comment token is not added to the token stream
        self.context.state = LexerState.START
    
    def _handle_fstring(self) -> None:
        """Handle f-strings."""
        # Simplified f-string handling
        if self._current_char() == '{':
            self._advance()
            if self._current_char() == '{':
                # Escaped {
                self._advance()
            else:
                # Start of expression
                self.context.state = LexerState.IN_FSTRING_EXPR
                self.context.paren_level = 1
        elif self._current_char() == '}':
            self._advance()
            if self._current_char() == '}':
                # Escaped }
                self._advance()
            else:
                self._error("Single '}' in f-string")
        elif self._current_char() == self._string_quote:
            # End of f-string
            self._advance()
            lexeme = self.source[self.start_pos:self.pos]
            self._add_token(TokenType.STRING, lexeme, lexeme[2:-1])
            self.context.state = LexerState.START
            self.context.fstring_stack.pop()
        else:
            self._advance()
    
    def _handle_fstring_expr(self) -> None:
        """Handle expressions inside f-strings."""
        # Simplified expression handling
        if self._current_char() == '{':
            self.context.paren_level += 1
            self._advance()
        elif self._current_char() == '}':
            self.context.paren_level -= 1
            if self.context.paren_level == 0:
                # End of expression
                self._advance()
                self.context.state = LexerState.IN_FSTRING
            else:
                self._advance()
        elif self._current_char() == '[':
            self.context.bracket_level += 1
            self._advance()
        elif self._current_char() == ']':
            if self.context.bracket_level == 0:
                self._error("Unmatched ']' in f-string expression")
            self.context.bracket_level -= 1
            self._advance()
        elif self._current_char() == '(':
            self.context.paren_level += 1
            self._advance()
        elif self._current_char() == ')':
            if self.context.paren_level == 0:
                self._error("Unmatched ')' in f-string expression")
            self.context.paren_level -= 1
            self._advance()
        elif self._current_char() == ':' and self.context.paren_level == 1 and self.context.bracket_level == 0:
            # Start of format specifier
            self.context.state = LexerState.IN_FSTRING_FORMAT_SPEC
            self._advance()
        else:
            self._advance()
    
    def _handle_fstring_format_spec(self) -> None:
        """Handle format specifiers in f-strings."""
        if self._current_char() == '}':
            self.context.paren_level -= 1
            if self.context.paren_level == 0:
                # End of format specifier and expression
                self._advance()
                self.context.state = LexerState.IN_FSTRING
            else:
                self._advance()
        elif self._current_char() == '{':
            self._advance()
            if self._current_char() == '{':
                # Escaped {
                self._advance()
            else:
                self.context.paren_level += 1
        elif self._current_char() == '}':
            self._advance()
            if self._current_char() == '}':
                # Escaped }
                self._advance()
            else:
                self._error("Single '}' in format string")
        else:
            self._advance()
    
    def _handle_operator_or_delimiter(self) -> None:
        """Handle operators and delimiters."""
        c = self._current_char()
        
        # Check for multi-character operators first
        if c in MULTI_CHAR_STARTS and not self._is_at_end(1):
            next_char = self.source[self.pos + 1]
            for seq, token_type in MULTI_CHAR_STARTS[c]:
                if len(seq) > 1 and self.pos + len(seq) <= len(self.source):
                    if self.source[self.pos:self.pos+len(seq)] == seq:
                        self._advance(len(seq))
                        self._add_token(token_type, seq)
                        return
        
        # Check for single-character tokens
        if c in SINGLE_CHAR_TOKENS:
            self._add_token(SINGLE_CHAR_TOKENS[c], c)
            self._advance()
            return
        
        # Unknown character
        self._error(f"Unexpected character: {c}")
    
    def _handle_newline(self) -> None:
        """Handle newlines and indentation."""
        # Get the newline sequence (\n, \r, or \r\n)
        newline = self._current_char()
        if newline == '\r' and self._peek() == '\n':
            newline = '\r\n'
            self._advance()
        
        self._add_token(TokenType.NEWLINE, newline)
        self._advance()
        
        # Reset column and increment line
        self.line += 1
        self.column = 1
        
        # Skip whitespace at beginning of line
        indent = 0
        while self._current_char() in WHITESPACE:
            if self._current_char() == '\t':
                # Tabs align to multiples of 8
                indent = (indent // 8 + 1) * 8
            else:
                indent += 1
            self._advance()
        
        # Skip comments and blank lines
        if self._current_char() in ('\n', '\r', '#'):
            return
        
        # Handle indentation
        current_indent = self.context.indentation_stack[-1]
        
        if indent > current_indent:
            # New indentation level
            self.context.indentation_stack.append(indent)
            self._add_token(TokenType.INDENT, ' ' * indent)
        elif indent < current_indent:
            # Dedent to a previous level
            while self.context.indentation_stack and self.context.indentation_stack[-1] > indent:
                self.context.indentation_stack.pop()
                self._add_token(TokenType.DEDENT, '')
            
            if self.context.indentation_stack[-1] != indent:
                self._error("Inconsistent indentation")
    
    def _add_token(self, token_type: TokenType, lexeme: str, literal: Any = None) -> None:
        """
        Add a token to the token list.
        
        Args:
            token_type: The type of the token.
            lexeme: The actual text from the source code.
            literal: The literal value of the token (for numbers, strings, etc.).
        """
        self.tokens.append(Token(
            type=token_type,
            lexeme=lexeme,
            literal=literal,
            line=self.start_line,
            column=self.start_column,
            filename=self.filename
        ))
    
    def _error(self, message: str) -> None:
        """
        Report a lexer error.
        
        Args:
            message: The error message.
        """
        error = LexerSyntaxError(
            message=message,
            line=self.start_line,
            column=self.start_column,
            filename=self.filename
        )
        self.errors.append(error)
        raise error
    
    def _warn(self, message: str) -> None:
        """
        Report a lexer warning.
        
        Args:
            message: The warning message.
        """
        warning = LexerWarning(f"{self.filename}:{self.start_line}:{self.start_column}: {message}")
        self.warnings.append(warning)
    
    def _advance(self, n: int = 1) -> None:
        """
        Advance the current position by n characters.
        
        Args:
            n: Number of characters to advance.
        """
        for _ in range(n):
            if not self._is_at_end():
                if self._current_char() in ('\n', '\r'):
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
    
    def _current_char(self) -> str:
        """Return the current character, or '\0' if at the end."""
        return self.source[self.pos] if self.pos < len(self.source) else '\0'
    
    def _peek(self, n: int = 1) -> str:
        """
        Peek ahead n characters.
        
        Args:
            n: Number of characters to peek ahead.
            
        Returns:
            The nth character ahead, or '\0' if at the end.
        """
        pos = self.pos + n
        return self.source[pos] if pos < len(self.source) else '\0'
    
    def _is_at_end(self, offset: int = 0) -> bool:
        """
        Check if the current position is at or beyond the end of the source.
        
        Args:
            offset: Optional offset from current position.
            
        Returns:
            True if at or beyond the end, False otherwise.
        """
        return (self.pos + offset) >= len(self.source)
    
    def _match_pattern(self, pattern: Pattern) -> bool:
        """
        Try to match a pattern at the current position.
        
        Args:
            pattern: Compiled regex pattern to match.
            
        Returns:
            True if the pattern matches, False otherwise.
        """
        match = pattern.match(self.source, self.pos)
        if match:
            self._current_match = match
            return True
        return False
    
    def _consume_whitespace(self) -> None:
        """Skip over whitespace characters."""
        while not self._is_at_end() and self._current_char() in WHITESPACE:
            self._advance()
    
    def _consume_until(self, chars: str) -> str:
        """
        Consume characters until one of the specified characters is found.
        
        Args:
            chars: String of characters to stop at.
            
        Returns:
            The consumed string (not including the stopping character).
        """
        start = self.pos
        while not self._is_at_end() and self._current_char() not in chars:
            self._advance()
        return self.source[start:self.pos]


def tokenize(source: str, filename: str = "<string>") -> List[Token]:
    """
    Tokenize source code into a list of tokens.
    
    This is a convenience function that creates a Lexer instance and
    calls its tokenize() method.
    
    Args:
        source: The source code to tokenize.
        filename: The name of the source file (for error messages).
        
    Returns:
        List of tokens.
    """
    lexer = Lexer(source, filename)
    return lexer.tokenize()
