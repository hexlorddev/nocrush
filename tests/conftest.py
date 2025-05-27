"""
Pytest configuration and fixtures for NooCrush tests.
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from noocrush.lexer import Scanner
from noocrush.parser import Parser
from noocrush.interpreter import Interpreter

@pytest.fixture
def scanner():
    """Fixture providing a Scanner instance."""
    return Scanner()

@pytest.fixture
def parser():
    """Fixture providing a Parser instance."""
    return Parser()

@pytest.fixture
def interpreter():
    """Fixture providing an Interpreter instance."""
    return Interpreter()

@pytest.fixture
def example_files():
    """Fixture providing paths to example files."""
    examples_dir = Path(__file__).parent.parent / "noocrush" / "examples"
    return {
        'hello_world': examples_dir / "hello_world.noo",
        'features': examples_dir / "features.noo"
    }

# Add command line options
def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )

def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line("markers", "slow: mark test as slow to run")

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
