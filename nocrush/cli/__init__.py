"""
Command Line Interface for NooCrush.
"""
import sys
import os
import argparse
from typing import Optional, List, Dict, Any
from pathlib import Path

class NooCrushCLI:
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands and options."""
        parser = argparse.ArgumentParser(
            prog="noocrush",
            description="NooCrush - A hybrid language combining Python, Rust, and JavaScript features"
        )
        
        # Global arguments
        parser.add_argument(
            '-v', '--version',
            action='store_true',
            help='show version information and exit'
        )
        
        # Subparsers for different commands
        subparsers = parser.add_subparsers(dest='command', help='command to execute')
        
        # Run command
        run_parser = subparsers.add_parser('run', help='run a NooCrush script')
        run_parser.add_argument(
            'file',
            type=str,
            help='NooCrush script to execute (.noo file)'
        )
        run_parser.add_argument(
            'args',
            nargs=argparse.REMAINDER,
            help='arguments to pass to the script'
        )
        
        # REPL command
        repl_parser = subparsers.add_parser('repl', help='start an interactive REPL')
        
        # Format command
        fmt_parser = subparsers.add_parser('fmt', help='format NooCrush code')
        fmt_parser.add_argument(
            'files',
            nargs='+',
            type=str,
            help='files or directories to format'
        )
        fmt_parser.add_argument(
            '--check',
            action='store_true',
            help='check if files need formatting (exit code 0 means no changes needed)'
        )
        
        # Lint command
        lint_parser = subparsers.add_parser('lint', help='lint NooCrush code')
        lint_parser.add_argument(
            'files',
            nargs='+',
            type=str,
            help='files or directories to lint'
        )
        
        # Test command
        test_parser = subparsers.add_parser('test', help='run tests')
        test_parser.add_argument(
            'pattern',
            nargs='?',
            default='*',
            help='test pattern to match (default: run all tests)'
        )
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Parse command line arguments."""
        return vars(self.parser.parse_args(args))
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments."""
        parsed_args = self.parse_args(args)
        
        if parsed_args.get('version'):
            from .. import __version__
            print(f"NooCrush v{__version__}")
            return 0
        
        command = parsed_args.get('command')
        
        if not command:
            self.parser.print_help()
            return 1
        
        try:
            if command == 'run':
                return self._run_script(parsed_args)
            elif command == 'repl':
                return self._start_repl()
            elif command == 'fmt':
                return self._format_code(parsed_args)
            elif command == 'lint':
                return self._lint_code(parsed_args)
            elif command == 'test':
                return self._run_tests(parsed_args)
            else:
                print(f"Unknown command: {command}")
                return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if parsed_args.get('debug'):
                import traceback
                traceback.print_exc()
            return 1
    
    def _run_script(self, args: Dict[str, Any]) -> int:
        """Run a NooCrush script."""
        from ..interpreter import run_file
        
        script_path = args['file']
        if not os.path.exists(script_path):
            print(f"Error: File not found: {script_path}", file=sys.stderr)
            return 1
        
        # Save command line arguments for the script
        sys.argv = [script_path] + args.get('args', [])
        
        try:
            run_file(script_path)
            return 0
        except Exception as e:
            print(f"Error executing {script_path}: {e}", file=sys.stderr)
            return 1
    
    def _start_repl(self) -> int:
        """Start the NooCrush REPL."""
        from ..interpreter import Interpreter
        from ..lexer import Scanner
        from ..parser import Parser
        
        print("NooCrush REPL (type 'exit' or 'quit' to exit)")
        print(f"Version {__import__('noocrush').__version__}\n")
        
        interpreter = Interpreter()
        
        while True:
            try:
                try:
                    source = input("noo> ").strip()
                except EOFError:
                    print("\nGoodbye!")
                    break
                
                if source.lower() in ('exit', 'quit'):
                    break
                if not source:
                    continue
                
                # Try to execute the input
                scanner = Scanner(source)
                tokens = scanner.scan_tokens()
                
                # Check for errors during scanning
                if any(t.type == TokenType.ERROR for t in tokens):
                    print("Error during scanning")
                    continue
                
                parser = Parser(tokens)
                statements = parser.parse()
                
                # Execute the parsed statements
                for stmt in statements:
                    result = interpreter._execute(stmt)
                    if result is not None and result.type != ValueType.NULL:
                        print(f"=> {result}")
                        
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to exit")
                continue
            except Exception as e:
                print(f"Error: {e}")
        
        return 0
    
    def _format_code(self, args: Dict[str, Any]) -> int:
        """Format NooCrush code."""
        print("Code formatting not yet implemented")
        return 0
    
    def _lint_code(self, args: Dict[str, Any]) -> int:
        """Lint NooCrush code."""
        print("Code linting not yet implemented")
        return 0
    
    def _run_tests(self, args: Dict[str, Any]) -> int:
        """Run tests."""
        print("Testing not yet implemented")
        return 0

def main() -> int:
    """Entry point for the CLI."""
    return NooCrushCLI().run()

if __name__ == "__main__":
    sys.exit(main())
