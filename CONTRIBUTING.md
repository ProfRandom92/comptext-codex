# Contributing to CompText-Codex

Thank you for your interest in contributing to CompText-Codex! 🎉

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs or suggest features
- Provide clear descriptions and examples
- Include version information and environment details

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit with clear messages (`git commit -m 'feat: add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Commit Message Convention
Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or modifications
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Testing
- Write tests for all new functionality
- Maintain or improve code coverage
- Run the full test suite before submitting

### Documentation
- Update documentation for API changes
- Add examples for new features
- Keep README.md up to date

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/comptext-codex.git
cd comptext-codex

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run with coverage
pytest --cov=comptext_codex
```

## Questions?

Feel free to open a discussion or reach out via GitHub Issues.

## Code of Conduct

Be respectful, inclusive, and collaborative. We're here to build something great together!
