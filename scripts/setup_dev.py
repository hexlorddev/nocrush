#!/usr/bin/env python3
"""
Development environment setup script for NooCrush.
This script helps set up a development environment with all necessary dependencies.
"""
import os
import sys
import subprocess
import platform
import shutil
import venv
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.upper():^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}")

def print_step(step):
    """Print a step with formatting."""
    print(f"\n{Colors.OKBLUE}==> {step}{Colors.ENDC}")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message and exit."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}", file=sys.stderr)
    sys.exit(1)

def run_command(command, cwd=None, shell=False):
    """Run a shell command and return the output."""
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd or PROJECT_ROOT,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print_error(f"Command failed: {' '.join(command) if isinstance(command, list) else command}\n{stderr}")
        
        return stdout.strip()
    except Exception as e:
        print_error(f"Error running command: {e}")

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print_header("Checking Prerequisites")
    
    # Check Python version
    required_python = (3, 8)
    if sys.version_info < required_python:
        print_error(f"Python {required_python[0]}.{required_python[1]}+ is required. Current: {sys.version}")
    
    print_success(f"Python {sys.version.split()[0]} detected")
    
    # Check for Git
    try:
        git_version = run_command(["git", "--version"])
        print_success(f"{git_version} detected")
    except FileNotFoundError:
        print_warning("Git is not installed. Some features may be limited.")
    
    # Check for Docker
    try:
        docker_version = run_command(["docker", "--version"])
        print_success(f"{docker_version} detected")
    except FileNotFoundError:
        print_warning("Docker is not installed. Container-based development will not be available.")
    
    # Check for Docker Compose
    try:
        compose_version = run_command(["docker-compose", "--version"])
        print_success(f"{compose_version} detected")
    except FileNotFoundError:
        print_warning("Docker Compose is not installed. Container-based development will not be available.")

def setup_virtualenv():
    """Set up a Python virtual environment."""
    print_header("Setting Up Virtual Environment")
    
    venv_dir = PROJECT_ROOT / ".venv"
    
    if venv_dir.exists():
        print_warning(f"Virtual environment already exists at {venv_dir}")
        if input("Recreate virtual environment? [y/N] ").lower() != 'y':
            return
        shutil.rmtree(venv_dir)
    
    print_step("Creating virtual environment...")
    venv.create(venv_dir, with_pip=True)
    
    # Get the correct pip path based on the OS
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip"
        python_path = venv_dir / "Scripts" / "python"
    else:
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    print_step("Upgrading pip and setuptools...")
    run_command([str(pip_path), "install", "--upgrade", "pip", "setuptools"])
    
    print_step("Installing development dependencies...")
    run_command([str(pip_path), "install", "-r", "requirements-dev.txt"])
    
    print_step("Installing package in development mode...")
    run_command([str(pip_path), "install", "-e", "."])
    
    print_success(f"Virtual environment set up at {venv_dir}")
    print_success(f"Activate it with: {'.venv\\Scripts\\activate' if platform.system() == 'Windows' else 'source .venv/bin/activate'}")

def setup_git_hooks():
    """Set up Git hooks."""
    print_header("Setting Up Git Hooks")
    
    git_dir = PROJECT_ROOT / ".git"
    hooks_dir = git_dir / "hooks"
    
    if not git_dir.exists():
        print_warning("This is not a Git repository. Skipping Git hooks setup.")
        return
    
    hooks_dir.mkdir(exist_ok=True)
    
    # Pre-commit hook
    pre_commit = hooks_dir / "pre-commit"
    with open(pre_commit, 'w') as f:
        f.write("""#!/bin/sh
# Run linters and tests before allowing a commit
set -e

echo "Running pre-commit checks..."

# Run linters
flake8 .
mypy .

# Run tests
pytest -v

echo "All checks passed!"
""")
    
    # Make the hook executable
    pre_commit.chmod(0o755)
    
    print_success("Git hooks set up successfully")

def main():
    """Main function."""
    print_header("NooCrush Development Environment Setup")
    print(f"Project root: {PROJECT_ROOT}")
    
    check_prerequisites()
    setup_virtualenv()
    setup_git_hooks()
    
    print_header("Setup Complete!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    print(f"   {'source .venv/bin/activate' if platform.system() != 'Windows' else '.\\venv\\Scripts\\activate'}")
    print("2. Run the tests:")
    print("   pytest -v")
    print("3. Start developing!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
        sys.exit(1)
