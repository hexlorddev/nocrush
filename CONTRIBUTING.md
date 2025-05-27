# Contributing to NooCrush

Thank you for your interest in contributing to NooCrush! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Environment Setup](#development-environment-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Code Review Process](#code-review-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check if the issue has already been reported in the [issue tracker](https://github.com/yourusername/noocrush/issues). If you find an open issue that addresses the problem, please add a comment with any additional information.

When creating a bug report, please include the following information:

1. A clear and descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Environment information (OS, Python version, etc.)
6. Any relevant error messages or logs

### Suggesting Enhancements

We welcome suggestions for new features and improvements. Before creating a feature request, please check if a similar feature has already been requested.

When suggesting an enhancement, please include:

1. A clear and descriptive title
2. A detailed description of the feature
3. Why this feature would be useful
4. Any examples of how it might be used
5. Any potential drawbacks or considerations

### Your First Code Contribution

If you're new to open source or the codebase, we recommend starting with issues labeled as "good first issue" or "help wanted". These are typically smaller, well-defined tasks that are good for new contributors.

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. Ensure the test suite passes (`noocrush test`).
3. Make sure your code follows our coding standards.
4. Add tests for your changes.
5. Update the documentation if necessary.
6. Ensure all tests pass.
7. Submit a pull request with a clear description of your changes.

## Development Environment Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/noocrush.git
   cd noocrush
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all function signatures
- Write docstrings following [Google style](https://google.github.io/styleguide/pyguide.html#381-docstrings)
- Keep lines under 100 characters
- Use `black` for code formatting
- Use `isort` for import sorting

## Testing

We use `pytest` for testing. To run the test suite:

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=noocrush tests/
```

## Documentation

We use Sphinx for documentation. To build the documentation:

```bash
cd docs
make html
```

Documentation will be available in `docs/_build/html`.

## Code Review Process

1. A maintainer will review your pull request.
2. You may receive feedback or be asked to make changes.
3. Once approved, a maintainer will merge your changes.

## Community

- Join our [Discord server](https://discord.gg/your-discord-invite)
- Follow us on [Twitter](https://twitter.com/NooCrushLang)
- Check out our [blog](https://noocrush.dev/blog) for updates

## License

By contributing to NooCrush, you agree that your contributions will be licensed under the [MIT License](LICENSE).
