"""
Error handling for the NooCrush language.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

class ErrorLevel:
    """Error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"

@dataclass
class SourceLocation:
    """Represents a location in source code."""
    file: Optional[str] = None
    line: int = 1
    column: int = 1
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column
        }

class ErrorCode:
    """Standard error codes for NooCrush."""
    # Lexer errors (1000-1999)
    UNEXPECTED_CHAR = 1001
    UNTERMINATED_STRING = 1002
    INVALID_NUMBER = 1003
    
    # Parser errors (2000-2999)
    UNEXPECTED_TOKEN = 2001
    EXPECTED_EXPRESSION = 2002
    EXPECTED_STATEMENT = 2003
    EXPECTED_IDENTIFIER = 2004
    EXPECTED_TYPE = 2005
    EXPECTED_LEFT_BRACE = 2006
    EXPECTED_RIGHT_BRACE = 2007
    EXPECTED_LEFT_PAREN = 2008
    EXPECTED_RIGHT_PAREN = 2009
    EXPECTED_SEMICOLON = 2010
    EXPECTED_COLON = 2011
    DUPLICATE_PARAMETER = 2012
    
    # Type errors (3000-3999)
    TYPE_MISMATCH = 3001
    UNDEFINED_VARIABLE = 3002
    UNDEFINED_FUNCTION = 3003
    UNDEFINED_PROPERTY = 3004
    INVALID_OPERATION = 3005
    NOT_CALLABLE = 3006
    ARGUMENT_COUNT_MISMATCH = 3007
    DUPLICATE_DECLARATION = 3008
    CONST_REASSIGNMENT = 3009
    
    # Runtime errors (4000-4999)
    DIVISION_BY_ZERO = 4001
    INDEX_OUT_OF_BOUNDS = 4002
    KEY_ERROR = 4003
    IMPORT_ERROR = 4004
    IO_ERROR = 4005
    
    # Internal errors (9000-9999)
    INTERNAL_ERROR = 9001

@dataclass
class Error:
    """Represents an error in the NooCrush language."""
    code: int
    message: str
    location: Optional[SourceLocation] = None
    level: str = ErrorLevel.ERROR
    hints: List[str] = None
    related: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.hints is None:
            self.hints = []
        if self.related is None:
            self.related = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "level": self.level,
            "location": self.location.to_dict() if self.location else None,
            "hints": self.hints,
            "related": self.related
        }
    
    def format(self, source: Optional[str] = None) -> str:
        """Format the error message with source context if available."""
        from ..utils import format_error
        
        if not self.location or not source:
            return self.message
        
        return format_error(
            message=self.message,
            line=self.location.line,
            col=self.location.column,
            file=self.location.file,
            code=source,
            context_lines=2
        )

class ErrorReporter:
    """Collects and reports errors during compilation or execution."""
    
    def __init__(self):
        self.errors: List[Error] = []
        self.warnings: List[Error] = []
        self.infos: List[Error] = []
    
    def add_error(
        self, 
        message: str, 
        code: int = ErrorCode.INTERNAL_ERROR,
        location: Optional[SourceLocation] = None,
        hints: Optional[List[str]] = None,
        related: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add an error to the reporter."""
        self.errors.append(Error(
            code=code,
            message=message,
            location=location,
            level=ErrorLevel.ERROR,
            hints=hints or [],
            related=related or []
        ))
    
    def add_warning(
        self, 
        message: str, 
        code: int = 0,
        location: Optional[SourceLocation] = None,
        hints: Optional[List[str]] = None,
        related: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add a warning to the reporter."""
        self.warnings.append(Error(
            code=code,
            message=message,
            location=location,
            level=ErrorLevel.WARNING,
            hints=hints or [],
            related=related or []
        ))
    
    def add_info(
        self, 
        message: str, 
        code: int = 0,
        location: Optional[SourceLocation] = None,
        hints: Optional[List[str]] = None,
        related: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add an info message to the reporter."""
        self.infos.append(Error(
            code=code,
            message=message,
            location=location,
            level=ErrorLevel.INFO,
            hints=hints or [],
            related=related or []
        ))
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_all_messages(self) -> List[Error]:
        """Get all messages in order of severity (errors, then warnings, then infos)."""
        return self.errors + self.warnings + self.infos
    
    def format_all(self, source: Optional[str] = None) -> List[str]:
        """Format all messages with source context if available."""
        return [msg.format(source) for msg in self.get_all_messages()]
    
    def clear(self) -> None:
        """Clear all messages."""
        self.errors.clear()
        self.warnings.clear()
        self.infos.clear()

def create_syntax_error(
    message: str,
    code: int = ErrorCode.UNEXPECTED_TOKEN,
    location: Optional[SourceLocation] = None,
    token_type: Optional[str] = None,
    expected: Optional[List[str]] = None
) -> Error:
    """Create a syntax error with helpful hints."""
    hints = []
    if token_type:
        hints.append(f"Found token: {token_type}")
    if expected:
        if len(expected) == 1:
            hints.append(f"Expected: {expected[0]}")
        elif expected:
            hints.append(f"Expected one of: {', '.join(expected)}")
    
    return Error(
        code=code,
        message=f"Syntax Error: {message}",
        location=location,
        level=ErrorLevel.ERROR,
        hints=hints
    )

def create_type_error(
    message: str,
    code: int = ErrorCode.TYPE_MISMATCH,
    location: Optional[SourceLocation] = None,
    expected: Optional[str] = None,
    actual: Optional[str] = None
) -> Error:
    """Create a type error with helpful hints."""
    hints = []
    if expected is not None:
        hints.append(f"Expected type: {expected}")
    if actual is not None:
        hints.append(f"Found type: {actual}")
    
    return Error(
        code=code,
        message=f"Type Error: {message}",
        location=location,
        level=ErrorLevel.ERROR,
        hints=hints
    )

def create_runtime_error(
    message: str,
    code: int = ErrorCode.INTERNAL_ERROR,
    location: Optional[SourceLocation] = None,
    context: Optional[Dict[str, Any]] = None
) -> Error:
    """Create a runtime error with context."""
    hints = []
    if context:
        for key, value in context.items():
            hints.append(f"{key}: {value}")
    
    return Error(
        code=code,
        message=f"Runtime Error: {message}",
        location=location,
        level=ErrorLevel.ERROR,
        hints=hints
    )
