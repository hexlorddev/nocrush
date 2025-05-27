#!/usr/bin/env python3
"""
Script to create a comprehensive directory structure for the NooCrush project.
"""
import os
from pathlib import Path
from typing import List, Dict, Union

class DirectoryStructure:
    """Class to manage directory structure creation."""
    
    def __init__(self, root: Union[str, Path]):
        """Initialize with root directory."""
        self.root = Path(root).resolve()
        
    def create_directories(self, structure: Dict[str, any]) -> None:
        """Create directory structure recursively."""
        self._create_directories(self.root, structure)
    
    def _create_directories(self, 
                          base: Path, 
                          structure: Union[Dict[str, any], List[str]], 
                          prefix: str = ""):
        """Recursively create directories."""
        if isinstance(structure, dict):
            for name, children in structure.items():
                path = base / name
                print(f"Creating directory: {prefix}{name}")
                path.mkdir(parents=True, exist_ok=True)
                self._create_directories(path, children, prefix + "  ")
        elif isinstance(structure, list):
            for name in structure:
                path = base / name
                print(f"Creating directory: {prefix}{name}")
                path.mkdir(parents=True, exist_ok=True)

def main():
    """Main function to create the directory structure."""
    # Define the directory structure
    structure = {
        "noocrush": {
            "core": {
                "ast": ["nodes", "visitors", "transformers"],
                "lexer": ["tokens", "scanner", "preprocessor"],
                "parser": ["grammar", "ast_builder", "error_handling"],
                "interpreter": ["runtime", "evaluator", "builtins"],
                "compiler": ["bytecode", "optimizer", "codegen"],
                "vm": ["opcodes", "interpreter", "garbage_collector"]
            },
            "stdlib": {
                "io": ["file", "network", "serialization"],
                "math": ["arithmetic", "random", "statistics"],
                "collections": ["list", "dict", "set", "queue"],
                "concurrent": ["threading", "processes", "async"],
                "os": ["path", "process", "env"],
                "datetime": ["date", "time", "timezone"],
                "re": ["matcher", "parser"],
                "json": ["encoder", "decoder"],
                "http": ["client", "server", "middleware"],
                "crypto": ["hash", "cipher", "signature"]
            },
            "frontend": {
                "cli": ["commands", "repl", "completion"],
                "gui": ["windows", "widgets", "themes"],
                "web": ["static", "templates", "api"]
            },
            "backend": {
                "server": ["api", "routing", "middleware"],
                "database": ["orm", "migrations", "query"],
                "cache": ["memory", "redis", "memcached"],
                "auth": ["jwt", "oauth", "permissions"]
            },
            "tools": {
                "debugger": ["breakpoints", "inspect", "profiler"],
                "formatter": ["pretty_print", "minifier"],
                "linter": ["rules", "fixers", "reporters"],
                "doc_generator": ["parser", "renderer", "templates"]
            },
            "utils": {
                "logging": ["handlers", "formatters", "filters"],
                "testing": ["mocks", "fixtures", "assertions"],
                "types": ["annotations", "validators", "converters"],
                "async_utils": ["tasks", "synchronization"]
            },
            "extensions": {
                "numpy": ["array_ops", "random", "linalg"],
                "pandas": ["dataframe", "series", "io"],
                "plotting": ["matplotlib", "plotly", "bokeh"],
                "ml": ["preprocessing", "models", "metrics"]
            },
            "config": {
                "parsers": ["json", "yaml", "toml", "env"],
                "loaders": ["file", "env", "vault"]
            },
            "i18n": {
                "locales": ["en_US", "es_ES", "fr_FR", "de_DE"],
                "formats": ["numbers", "dates", "plurals"]
            },
            "errors": {
                "handlers": ["cli", "web", "logging"],
                "types": ["syntax", "runtime", "validation"]
            },
            "types": {
                "primitives": [],
                "collections": [],
                "functions": [],
                "classes": []
            },
            "examples": {
                "beginner": [],
                "intermediate": [],
                "advanced": [],
                "web": [],
                "data_science": [],
                "games": []
            }
        },
        "tests": {
            "unit": {
                "core": ["ast", "lexer", "parser", "interpreter", "compiler", "vm"],
                "stdlib": ["io", "math", "collections", "concurrent", "os", "datetime"],
                "frontend": ["cli", "gui", "web"],
                "backend": ["server", "database", "cache", "auth"]
            },
            "integration": {
                "api": [],
                "database": [],
                "performance": [],
                "security": []
            },
            "e2e": {
                "web": [],
                "cli": [],
                "mobile": []
            },
            "benchmarks": {
                "performance": [],
                "memory": [],
                "load": []
            },
            "fixtures": {
                "data": [],
                "mocks": []
            },
            "test_utils": []
        },
        "docs": {
            "source": {
                "getting_started": [],
                "tutorials": [],
                "how_to_guides": [],
                "reference": {
                    "api": [],
                    "cli": [],
                    "configuration": []
                },
                "explanation": [],
                "changelog": []
            },
            "build": {
                "html": [],
                "latex": [],
                "man": [],
                "epub": []
            },
            "templates": [],
            "static": {
                "css": [],
                "js": [],
                "images": []
            },
            "api": {
                "modules": [],
                "classes": [],
                "functions": []
            }
        },
        "scripts": {
            "dev": [],
            "build": [],
            "deploy": [],
            "maintenance": [],
            "analysis": [],
            "benchmarking": []
        },
        "tools": {
            "code_generation": [],
            "documentation": [],
            "testing": [],
            "profiling": [],
            "packaging": []
        },
        "resources": {
            "images": [],
            "fonts": [],
            "templates": [],
            "locales": [],
            "config": []
        },
        "deploy": {
            "docker": [],
            "kubernetes": {
                "manifests": [],
                "helm": []
            },
            "terraform": {
                "modules": [],
                "environments": {
                    "dev": [],
                    "staging": [],
                    "prod": []
                }
            },
            "ansible": {
                "playbooks": [],
                "roles": [],
                "inventory": []
            },
            "cloud": {
                "aws": [],
                "gcp": [],
                "azure": []
            }
        },
        "benchmarks": {
            "performance": [],
            "memory_usage": [],
            "load_testing": [],
            "comparison": []
        },
        "docker": {
            "development": [],
            "production": [],
            "testing": [],
            "services": []
        },
        ".github": {
            "workflows": [],
            "ISSUE_TEMPLATE": [],
            "PULL_REQUEST_TEMPLATE": []
        },
        "examples": {
            "basic": [],
            "web": [],
            "data_science": [],
            "games": [],
            "tutorials": []
        },
        "templates": {
            "project": [],
            "module": [],
            "test": [],
            "documentation": []
        },
        "reports": {
            "coverage": [],
            "complexity": [],
            "performance": [],
            "security": []
        },
        "logs": {
            "app": [],
            "server": [],
            "debug": []
        },
        "build": {
            "dist": [],
            "lib": [],
            "include": []
        },
        "dist": [],
        "site": []
    }

    # Create the directory structure
    root_dir = Path(__file__).parent.parent
    print(f"Creating directory structure in: {root_dir}")
    
    dir_structure = DirectoryStructure(root_dir)
    dir_structure.create_directories(structure)
    
    # Create some initial files
    create_initial_files(root_dir)
    
    print("\nDirectory structure created successfully!")

def create_initial_files(root_dir: Path) -> None:
    """Create some initial files in the directory structure."""
    # Create README.md
    readme_content = """# NooCrush

A powerful, high-level programming language with a focus on simplicity and productivity.

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- git

### Installation

```bash
git clone https://github.com/yourusername/noocrush.git
cd noocrush
pip install -e .
```

### Running the Interpreter

```bash
noocrush
```

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linter
flake8

# Run type checker
mypy .
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"""
    
    with open(root_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create empty __init__.py files
    for root, dirs, _ in os.walk(root_dir / "noocrush"):
        for dir_name in dirs:
            init_file = Path(root) / dir_name / "__init__.py"
            init_file.parent.mkdir(parents=True, exist_ok=True)
            if not init_file.exists():
                init_file.touch()
    
    # Create empty __init__.py in test directories
    for root, dirs, _ in os.walk(root_dir / "tests"):
        for dir_name in dirs:
            init_file = Path(root) / dir_name / "__init__.py"
            init_file.parent.mkdir(parents=True, exist_ok=True)
            if not init_file.exists():
                init_file.touch()

if __name__ == "__main__":
    main()
