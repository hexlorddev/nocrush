#!/usr/bin/env python3
"""
NooCrush - A hybrid language combining Python, Rust, and JavaScript features.
"""
import sys
from .interpreter import run_file

def main():
    if len(sys.argv) > 1:
        # Run the specified file
        run_file(sys.argv[1])
    else:
        # Start REPL
        print("NooCrush REPL (type 'exit' to quit)")
        while True:
            try:
                source = input("> ")
                if source.strip().lower() in ['exit', 'quit']:
                    break
                # For now, just print the source
                # In a real implementation, you would parse and execute the source
                print(f"You entered: {source}")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
