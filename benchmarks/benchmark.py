#!/usr/bin/env python3
"""
Performance benchmarking for the NooCrush interpreter.
"""
import time
import timeit
import statistics
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from noocrush.interpreter import Interpreter
from noocrush.lexer import Scanner
from noocrush.parser import Parser

class BenchmarkResult:
    """Class to store benchmark results."""
    
    def __init__(self, name: str):
        self.name = name
        self.times: List[float] = []
        self.memory_usage: List[float] = []
        self.metrics: Dict[str, Any] = {}
    
    def add_time(self, elapsed: float):
        """Add a time measurement."""
        self.times.append(elapsed)
    
    def add_memory(self, memory: float):
        """Add a memory usage measurement."""
        self.memory_usage.append(memory)
    
    def add_metric(self, name: str, value: Any):
        """Add a custom metric."""
        self.metrics[name] = value
    
    @property
    def stats(self) -> Dict[str, float]:
        """Calculate statistics for the benchmark."""
        if not self.times:
            return {}
            
        return {
            "name": self.name,
            "runs": len(self.times),
            "min": min(self.times) * 1000,  # Convert to ms
            "max": max(self.times) * 1000,
            "mean": statistics.mean(self.times) * 1000,
            "median": statistics.median(self.times) * 1000,
            "stdev": statistics.stdev(self.times) * 1000 if len(self.times) > 1 else 0,
            "total": sum(self.times) * 1000,
        }

class BenchmarkSuite:
    """A collection of benchmarks."""
    
    def __init__(self):
        self.results: Dict[str, BenchmarkResult] = {}
        self.interpreter = Interpreter()
    
    def add_benchmark(self, name: str, code: str, setup: str = "", iterations: int = 10):
        """Add a benchmark to the suite."""
        if name in self.results:
            raise ValueError(f"Benchmark '{name}' already exists")
        
        result = BenchmarkResult(name)
        self.results[name] = result
        
        # Compile the code once
        scanner = Scanner()
        scanner.source = code
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        
        # Setup code if provided
        if setup:
            setup_scanner = Scanner()
            setup_scanner.source = setup
            setup_tokens = setup_scanner.scan_tokens()
            setup_parser = Parser(setup_tokens)
            setup_statements = setup_parser.parse()
            self.interpreter.interpret(setup_statements)
        
        # Warm-up run
        try:
            self.interpreter.interpret(statements)
        except Exception as e:
            print(f"Error in benchmark '{name}': {e}")
            return
        
        # Run the benchmark
        for _ in range(iterations):
            start_time = time.perf_counter()
            self.interpreter.interpret(statements)
            elapsed = time.perf_counter() - start_time
            result.add_time(elapsed)
    
    def add_benchmark_from_file(self, name: str, filepath: Path, setup: str = "", iterations: int = 10):
        """Add a benchmark from a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        self.add_benchmark(name, code, setup, iterations)
    
    def run_benchmark(self, name: str, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """Run a benchmark with a custom function."""
        result = BenchmarkResult(name)
        
        # Warm-up
        func(*args, **kwargs)
        
        # Run benchmark
        for _ in range(10):  # Default to 10 iterations
            start_time = time.perf_counter()
            func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            result.add_time(elapsed)
        
        self.results[name] = result
        return result
    
    def get_results(self) -> Dict[str, Dict[str, float]]:
        """Get all benchmark results."""
        return {name: result.stats for name, result in self.results.items()}
    
    def print_results(self):
        """Print benchmark results in a table."""
        results = self.get_results()
        if not results:
            print("No benchmark results to display.")
            return
        
        # Prepare data for tabular display
        headers = ["Benchmark", "Runs", "Min (ms)", "Mean (ms)", "Max (ms)", "Stdev (ms)"]
        rows = []
        
        for name, stats in results.items():
            rows.append([
                name,
                stats["runs"],
                f"{stats['min']:.4f}",
                f"{stats['mean']:.4f}",
                f"{stats['max']:.4f}",
                f"{stats['stdev']:.4f}" if stats['runs'] > 1 else "N/A"
            ])
        
        # Calculate column widths
        col_widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
        
        # Print header
        header = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        print("\n" + "=" * len(header))
        print(header)
        print("=" * len(header))
        
        # Print rows
        for row in rows:
            print("  ".join(str(x).ljust(w) for x, w in zip(row, col_widths)))
        
        print("=" * len(header) + "\n")
    
    def save_results(self, filepath: Path):
        """Save benchmark results to a JSON file."""
        results = self.get_results()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filepath}")

def fibonacci_benchmark():
    """Benchmark for Fibonacci sequence calculation."""
    code = """
    fn fib(n) {
        if (n <= 1) return n;
        return fib(n - 1) + fib(n - 2);
    }
    fib(20);
    """
    return code

def list_operations_benchmark():
    """Benchmark for list operations."""
    code = """
    let list = [];
    for (let i = 0; i < 1000; i = i + 1) {
        list.push(i);
    }
    
    let sum = 0;
    for (let i = 0; i < list.length(); i = i + 1) {
        sum = sum + list[i];
    }
    sum
    """
    return code

def string_operations_benchmark():
    """Benchmark for string operations."""
    code = """
    let str = "";
    for (let i = 0; i < 1000; i = i + 1) {
        str = str + i.toString();
    }
    str.length()
    """
    return code

def main():
    """Main function to run benchmarks."""
    parser = argparse.ArgumentParser(description='Run NooCrush benchmarks')
    parser.add_argument('--output', '-o', type=Path, help='Output file for benchmark results (JSON)')
    parser.add_argument('--iterations', '-n', type=int, default=10, help='Number of iterations per benchmark')
    parser.add_argument('--benchmark', '-b', action='append', choices=['all', 'fibonacci', 'list', 'string'], 
                       help='Specific benchmarks to run')
    args = parser.parse_args()
    
    # Default to all benchmarks if none specified
    if not args.benchmark or 'all' in args.benchmark:
        benchmarks_to_run = ['fibonacci', 'list', 'string']
    else:
        benchmarks_to_run = args.benchmark
    
    suite = BenchmarkSuite()
    
    # Add benchmarks
    if 'fibonacci' in benchmarks_to_run:
        suite.add_benchmark("Fibonacci (20)", fibonacci_benchmark(), iterations=args.iterations)
    
    if 'list' in benchmarks_to_run:
        suite.add_benchmark("List Operations", list_operations_benchmark(), iterations=args.iterations)
    
    if 'string' in benchmarks_to_run:
        suite.add_benchmark("String Operations", string_operations_benchmark(), iterations=args.iterations)
    
    # Print results
    suite.print_results()
    
    # Save results if output file is specified
    if args.output:
        suite.save_results(args.output)

if __name__ == "__main__":
    main()
