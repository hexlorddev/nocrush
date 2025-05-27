""
Utility functions for the NooCrush language implementation.
"""
import os
import sys
import inspect
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable, Union
from pathlib import Path

T = TypeVar('T')

def ensure_list(value: Any) -> List[Any]:
    """Ensure the value is a list. If it's not, wrap it in a list."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]

def find_files(directory: Union[str, Path], 
               extensions: Optional[List[str]] = None,
               recursive: bool = True) -> List[Path]:
    """
    Find files in a directory with the given extensions.
    
    Args:
        directory: Directory to search in
        extensions: List of file extensions to include (with leading .)
        recursive: Whether to search recursively
        
    Returns:
        List of Path objects matching the criteria
    """
    if extensions is None:
        extensions = ['.noo']
    
    directory = Path(directory)
    if not directory.is_dir():
        return []
    
    if recursive:
        return [
            p for p in directory.rglob('*')
            if p.is_file() and p.suffix.lower() in extensions
        ]
    else:
        return [
            p for p in directory.glob('*')
            if p.is_file() and p.suffix.lower() in extensions
        ]

def get_class_that_defined_method(meth: Callable) -> Optional[type]:
    """Get the class that defines a method."""
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    
    if inspect.isfunction(meth):
        cls = getattr(
            inspect.getmodule(meth),
            meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
            None
        )
        if isinstance(cls, type):
            return cls
    
    return None

def format_error(message: str, line: int = 0, col: int = 0, 
                 file: Optional[str] = None, code: Optional[str] = None,
                 context_lines: int = 2) -> str:
    """
    Format an error message with context.
    
    Args:
        message: Error message
        line: Line number (1-based)
        col: Column number (1-based)
        file: File path
        code: Source code
        context_lines: Number of context lines to show
        
    Returns:
        Formatted error message
    """
    parts = []
    
    # Add file and position info
    if file:
        parts.append(f"{file}:")
    if line > 0:
        parts.append(f"{line}:")
        if col > 0:
            parts.append(f"{col}:")
    
    if parts:
        parts[-1] = parts[-1] + " "
    
    parts.append(f"error: {message}")
    
    # Add code context if available
    if code and line > 0:
        lines = code.splitlines()
        start_line = max(1, line - context_lines)
        end_line = min(len(lines), line + context_lines + 1)
        
        # Add context lines before the error
        for i in range(start_line, line):
            parts.append(f"{i:4d} | {lines[i-1]}")
        
        # Add the error line with a pointer
        if line <= len(lines):
            error_line = lines[line-1].replace('\t', ' ')
            parts.append(f"{line:4d} | {error_line}")
            if col > 0:
                parts.append(" " * (col + 6) + "^")
        
        # Add context lines after the error
        for i in range(line + 1, end_line + 1):
            parts.append(f"{i:4d} | {lines[i-1]}")
    
    return "
".join(parts)

def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Return the singular or plural form of a word based on the count."""
    if count == 1:
        return f"{count} {singular}"
    return f"{count} {plural if plural else singular + 's'}"

def get_terminal_width() -> int:
    """Get the width of the terminal in columns."""
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except:
        return 80  # Default width

def print_boxed(text: str, padding: int = 1, char: str = '#') -> None:
    """Print text in a box."""
    width = get_terminal_width()
    text_width = width - 4 - (padding * 2)
    
    # Split text into lines
    lines = []
    for line in text.split('\n'):
        while len(line) > text_width:
            # Try to find a good place to break the line
            break_at = line.rfind(' ', 0, text_width + 1)
            if break_at == -1:  # No space found, force break
                break_at = text_width
            lines.append(line[:break_at].strip())
            line = line[break_at:].strip()
        if line:
            lines.append(line)
    
    # Calculate box width
    max_line = max(len(line) for line in lines) if lines else 0
    box_width = max_line + (padding * 2)
    
    # Print the box
    print(char * (box_width + 4))
    for _ in range(padding):
        print(f"{char}{' ' * (box_width + 2)}{char}")
    
    for line in lines:
        spaces = box_width - len(line)
        left_pad = spaces // 2
        right_pad = spaces - left_pad
        print(f"{char} {' ' * left_pad}{line}{' ' * right_pad} {char}")
    
    for _ in range(padding):
        print(f"{char}{' ' * (box_width + 2)}{char}")
    print(char * (box_width + 4))
