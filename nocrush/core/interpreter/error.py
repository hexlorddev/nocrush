"""
Error handling for the NooCrush interpreter.
"""
from typing import Optional, List, Dict, Any, Type, Union
import sys
import traceback
from dataclasses import dataclass


class InterpreterError(Exception):
    """Base class for all NooCrush interpreter errors."""
    pass


class RuntimeError(InterpreterError):
    """Raised when a runtime error occurs during interpretation."""
    def __init__(self, message: str, token=None, context: str = None):
        self.message = message
        self.token = token
        self.context = context
        self.stack: List[Dict[str, Any]] = []
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.token:
            location = f"line {self.token.line}"
            if self.token.lexeme:
                location += f" at '{self.token.lexeme}'"
            return f"[RuntimeError] {location}: {self.message}"
        return f"[RuntimeError] {self.message}"


class NameError(InterpreterError):
    """Raised when a variable name is not found."""
    def __init__(self, name: str, message: str = None):
        self.name = name
        self.message = message or f"Name '{name}' is not defined"
        super().__init__(self.message)


class TypeError(InterpreterError):
    """Raised when an operation is performed on an inappropriate type."""
    def __init__(self, message: str, expected: str = None, got: str = None):
        if expected and got:
            message = f"Expected {expected}, got {got}"
        self.message = message
        super().__init__(self.message)


class ValueError(InterpreterError):
    """Raised when an operation receives an argument with the right type but inappropriate value."""
    pass


class ZeroDivisionError(InterpreterError):
    """Raised when division or modulo by zero occurs."""
    def __init__(self, message: str = "Division by zero"):
        self.message = message
        super().__init__(self.message)


class IndexError(InterpreterError):
    """Raised when a sequence subscript is out of range."""
    def __init__(self, message: str = "Index out of range"):
        self.message = message
        super().__init__(self.message)


class KeyError(InterpreterError):
    """Raised when a dictionary key is not found."""
    def __init__(self, key, message: str = None):
        self.key = key
        self.message = message or f"Key '{key}' not found"
        super().__init__(self.message)


class AttributeError(InterpreterError):
    """Raised when an attribute reference or assignment fails."""
    def __init__(self, obj: Any, name: str, message: str = None):
        self.obj = obj
        self.name = name
        self.message = message or f"'{type(obj).__name__}' object has no attribute '{name}'"
        super().__init__(self.message)


class StopIteration(InterpreterError):
    """Raised by built-in next() to signal the end of iteration."""
    pass


class ImportError(InterpreterError):
    """Raised when an import statement fails."""
    def __init__(self, name: str, message: str = None):
        self.name = name
        self.message = message or f"Cannot import '{name}'"
        super().__init__(self.message)


class AssertionError(InterpreterError):
    """Raised when an assert statement fails."""
    def __init__(self, message: str = "Assertion failed"):
        self.message = message
        super().__init__(self.message)


class SyntaxError(InterpreterError):
    """Raised when the parser encounters a syntax error."""
    def __init__(self, message: str, line: int = None, where: str = None):
        self.message = message
        self.line = line
        self.where = where
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.line is not None:
            location = f"line {self.line}"
            if self.where:
                location += f" at '{self.where}'"
            return f"[SyntaxError] {location}: {self.message}"
        return f"[SyntaxError] {self.message}"


@dataclass
class ErrorInfo:
    """Stores information about an error that occurred during execution."""
    type: Type[Exception]
    message: str
    line: int
    column: int = 0
    filename: str = "<script>"
    context: str = None
    traceback: str = None


class ErrorReporter:
    ""
    Handles error reporting and formatting for the interpreter.
    """
    
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.errors: List[ErrorInfo] = []
    
    def reset(self) -> None:
        """Reset the error state."""
        self.had_error = False
        self.had_runtime_error = False
        self.errors.clear()
    
    def error(self, line: int, message: str, where: str = None) -> None:
        """
        Report a generic error.
        
        Args:
            line: Line number where the error occurred.
            message: Error message.
            where: Additional context about where the error occurred.
        """
        self._report(line, "", message, where)
    
    def syntax_error(self, token, message: str) -> None:
        """
        Report a syntax error.
        
        Args:
            token: The token where the error occurred.
            message: Error message.
        """
        where = token.lexeme if token.lexeme else ""
        self._report(token.line, "SyntaxError", message, where)
    
    def runtime_error(self, error: RuntimeError) -> None:
        """
        Report a runtime error.
        
        Args:
            error: The RuntimeError that occurred.
        """
        if error.token:
            self._report(error.token.line, "RuntimeError", error.message, error.token.lexeme)
        else:
            self._report(0, "RuntimeError", error.message)
        
        self.had_runtime_error = True
    
    def type_error(self, token, message: str) -> None:
        """
        Report a type error.
        
        Args:
            token: The token where the error occurred.
            message: Error message.
        """
        self._report(token.line, "TypeError", message, token.lexeme)
    
    def _report(self, line: int, error_type: str, message: str, where: str = None) -> None:
        """
        Internal method to report an error.
        
        Args:
            line: Line number where the error occurred.
            error_type: Type of error (e.g., 'SyntaxError', 'RuntimeError').
            message: Error message.
            where: Additional context about where the error occurred.
        """
        self.had_error = True
        
        # Format the error message
        parts = []
        if line > 0:
            parts.append(f"[line {line}]")
        
        if where:
            parts.append(f" at '{where}'")
        
        if parts:
            parts.append(": ")
        
        if error_type:
            parts.append(f"{error_type}: ")
        
        parts.append(message)
        
        # Print the error
        error_message = "".join(parts)
        print(error_message, file=sys.stderr)
        
        # Store the error
        error_info = ErrorInfo(
            type=type(error_message, (Exception,), {}),
            message=error_message,
            line=line,
            context=where
        )
        self.errors.append(error_info)
    
    def format_traceback(self, error: Exception) -> str:
        """
        Format a traceback for an exception.
        
        Args:
            error: The exception that was raised.
            
        Returns:
            Formatted traceback as a string.
        """
        try:
            import traceback
            return "".join(traceback.format_exception(type(error), error, error.__traceback__))
        except Exception:
            return f"{type(error).__name__}: {error}"
    
    def has_errors(self) -> bool:
        """Check if any errors have been reported."""
        return self.had_error or self.had_runtime_error
    
    def get_errors(self) -> List[ErrorInfo]:
        """Get a list of all reported errors."""
        return self.errors.copy()
    
    def clear_errors(self) -> None:
        """Clear all reported errors."""
        self.had_error = False
        self.had_runtime_error = False
        self.errors.clear()


# Global error reporter instance
error_reporter = ErrorReporter()


def report_error(line: int, message: str, where: str = None) -> None:
    """
    Report an error to the global error reporter.
    
    Args:
        line: Line number where the error occurred.
        message: Error message.
        where: Additional context about where the error occurred.
    """
    error_reporter.error(line, message, where)


def report_syntax_error(token, message: str) -> None:
    """
    Report a syntax error to the global error reporter.
    
    Args:
        token: The token where the error occurred.
        message: Error message.
    """
    error_reporter.syntax_error(token, message)


def report_runtime_error(error: RuntimeError) -> None:
    """
    Report a runtime error to the global error reporter.
    
    Args:
        error: The RuntimeError that occurred.
    """
    error_reporter.runtime_error(error)


def report_type_error(token, message: str) -> None:
    """
    Report a type error to the global error reporter.
    
    Args:
        token: The token where the error occurred.
        message: Error message.
    """
    error_reporter.type_error(token, message)


def had_error() -> bool:
    """Check if any errors have been reported."""
    return error_reporter.has_errors()


def clear_errors() -> None:
    """Clear all reported errors."""
    error_reporter.clear_errors()
