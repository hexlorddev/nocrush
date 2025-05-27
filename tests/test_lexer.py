"""
Tests for the NooCrush lexer.
"""
import pytest
from noocrush.lexer import Scanner, TokenType

# Test cases for lexer
def test_basic_tokens(scanner):
    """Test basic token recognition."""
    source = """
    let x = 42;
    const name = "NooCrush";
    if (x > 0) {
        print(name);
    }
    """
    scanner.source = source
    tokens = scanner.scan_tokens()
    
    # Check token types in sequence
    expected_types = [
        TokenType.LET, TokenType.IDENTIFIER, TokenType.EQUAL, TokenType.NUMBER, TokenType.SEMICOLON,
        TokenType.CONST, TokenType.IDENTIFIER, TokenType.EQUAL, TokenType.STRING, TokenType.SEMICOLON,
        TokenType.IF, TokenType.LEFT_PAREN, TokenType.IDENTIFIER, TokenType.GREATER, 
        TokenType.NUMBER, TokenType.RIGHT_PAREN, TokenType.LEFT_BRACE,
        TokenType.IDENTIFIER, TokenType.LEFT_PAREN, TokenType.IDENTIFIER, TokenType.RIGHT_PAREN, 
        TokenType.SEMICOLON,
        TokenType.RIGHT_BRACE,
        TokenType.EOF
    ]
    
    for i, token in enumerate(tokens):
        if i < len(expected_types):
            assert token.type == expected_types[i], f"Token {i} type mismatch: {token.type} != {expected_types[i]}"

def test_number_literals(scanner):
    """Test number literal tokens."""
    source = "42 3.14 0.5 1e10 1.5e-3"
    scanner.source = source
    tokens = scanner.scan_tokens()
    
    # Skip EOF token
    tokens = [t for t in tokens if t.type != TokenType.EOF]
    
    assert len(tokens) == 5
    assert tokens[0].lexeme == "42"
    assert tokens[1].lexeme == "3.14"
    assert tokens[2].lexeme == "0.5"
    assert tokens[3].lexeme == "1e10"
    assert tokens[4].lexeme == "1.5e-3"

def test_string_literals(scanner):
    """Test string literal tokens."""
    source = '"Hello, World!" "Escaped \\"quote\\"" "Multi\\nline"'
    scanner.source = source
    tokens = scanner.scan_tokens()
    
    # Skip EOF token
    tokens = [t for t in tokens if t.type == TokenType.STRING]
    
    assert len(tokens) == 3
    assert tokens[0].literal == "Hello, World!"
    assert tokens[1].literal == 'Escaped \"quote\"'
    assert tokens[2].literal == 'Multi\nline'

def test_operators(scanner):
    """Test operator tokens."""
    source = "+ - * / % = == != < <= > >= ! && ||"
    scanner.source = source
    tokens = scanner.scan_tokens()
    
    expected_types = [
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, 
        TokenType.PERCENT, TokenType.EQUAL, TokenType.EQUAL_EQUAL, 
        TokenType.BANG_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
        TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.BANG,
        TokenType.AND, TokenType.OR, TokenType.EOF
    ]
    
    for i, token in enumerate(tokens):
        if i < len(expected_types):
            assert token.type == expected_types[i], f"Token {i} type mismatch: {token.type} != {expected_types[i]}"

def test_comments(scanner):
    """Test comment handling."""
    source = """
    // This is a comment
    let x = 42; // End of line comment
    /* Multi-line
       comment */
    let y = 3.14;
    """
    scanner.source = source
    tokens = scanner.scan_tokens()
    
    # We should only have the variable declarations, not the comments
    token_types = [t.type for t in tokens]
    assert TokenType.COMMENT not in token_types
    assert TokenType.LET in token_types
    assert TokenType.NUMBER in token_types
    assert TokenType.SEMICOLON in token_types

# Add more test cases for error handling, edge cases, etc.

# Mark slow tests with @pytest.mark.slow
@pytest.mark.slow
def test_large_source_file(scanner):
    """Test lexing a large source file."""
    source = "let x = 42;\n" * 1000  # 1000 lines of code
    scanner.source = source
    tokens = scanner.scan_tokens()
    
    # Should have 1000 LET, 1000 IDENTIFIER, 1000 EQUAL, 1000 NUMBER, 1000 SEMICOLON, 1 EOF
    assert len([t for t in tokens if t.type == TokenType.LET]) == 1000
    assert len([t for t in tokens if t.type == TokenType.IDENTIFIER]) == 1000
    assert len([t for t in tokens if t.type == TokenType.EQUAL]) == 1000
    assert len([t for t in tokens if t.type == TokenType.NUMBER]) == 1000
    assert len([t for t in tokens if t.type == TokenType.SEMICOLON]) == 1000
    assert tokens[-1].type == TokenType.EOF
