# Contributing to CompText-Codex

Thank you for considering contributing to CompText-Codex! 🎉

## Ways to Contribute

### 1. Report Bugs 🐛
- Use GitHub Issues
- Include clear description and reproduction steps
- Provide code examples if applicable

### 2. Suggest Features 💡
- Open a discussion or issue
- Explain the use case
- Provide example syntax if proposing new commands

### 3. Improve Documentation 📝
- Fix typos or unclear explanations
- Add examples
- Translate documentation

### 4. Submit Code 🚀
- Fix bugs
- Implement new features
- Add new modules or commands

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/comptext-codex.git
cd comptext-codex
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

---

## Code Guidelines

### Python Style
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for all functions/classes

```python
def parse_command(command: str, context: dict) -> dict:
    """Parse a CompText command into executable structure.

    Args:
        command: The CompText command string
        context: Execution context with variables and settings

    Returns:
        Parsed command dictionary with action and parameters

    Raises:
        SyntaxError: If command syntax is invalid
    """
    pass
```

### Testing
- Write tests for all new features
- Maintain 90%+ code coverage
- Use pytest fixtures for common setups

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest --cov=comptext --cov-report=html

# Run specific test
pytest tests/test_module_b.py::test_code_analysis
```

### Documentation
- Update relevant .md files
- Add docstrings to code
- Include usage examples

---

## Pull Request Process

### 1. Before Submitting

✅ All tests pass
✅ Code follows style guidelines
✅ Documentation is updated
✅ Commit messages are clear

### 2. Commit Message Format

```
type(scope): brief description

Detailed explanation if needed.

Fixes #issue_number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Formatting changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(module-b): add code complexity analysis

Implements cyclomatic complexity calculation for Python code.

Fixes #42
```

```
fix(parser): handle edge case with nested brackets

The parser was failing when commands contained nested brackets.
This fix properly tracks bracket depth during parsing.

Fixes #105
```

### 3. Submit PR

1. Push your branch to GitHub
2. Open Pull Request against `main` branch
3. Fill out PR template
4. Link related issues
5. Wait for review

### 4. Review Process

- Maintainers will review within 48 hours
- Address feedback promptly
- Be open to suggestions
- Once approved, PR will be merged

---

## Adding New Modules

### Module Structure

```python
# comptext/modules/module_x.py

from typing import Dict, Any
from comptext.base import BaseModule

class ModuleX(BaseModule):
    """Description of Module X functionality."""

    def __init__(self):
        super().__init__(module_id='X', name='Your Module Name')
        self.register_commands()

    def register_commands(self):
        """Register all commands in this module."""
        self.add_command('YOUR_COMMAND', self.your_command)

    def your_command(self, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute YOUR_COMMAND.

        Args:
            params: Command parameters
            context: Execution context

        Returns:
            Command result
        """
        # Implementation
        pass
```

### Add Tests

```python
# tests/test_module_x.py

import pytest
from comptext.modules.module_x import ModuleX

def test_your_command():
    module = ModuleX()
    result = module.your_command(
        params={'param1': 'value1'},
        context={}
    )
    assert result is not None
```

### Update Documentation

Add to `docs/MODULES.md`:
```markdown
## Module X - Your Module Name

### Commands

#### @YOUR_COMMAND
Description of what this command does.

**Syntax:**
\`\`\`
@YOUR_COMMAND[param1, param2=value]
\`\`\`

**Example:**
\`\`\`python
command = "@YOUR_COMMAND[param1=test]"
result = parser.execute(command)
\`\`\`
```

---

## Code Review Checklist

### For Reviewers
- [ ] Code follows project style
- [ ] Tests are comprehensive
- [ ] Documentation is clear
- [ ] No breaking changes (or clearly documented)
- [ ] Performance considerations addressed

### For Contributors
- [ ] Self-reviewed my code
- [ ] Commented complex logic
- [ ] Updated documentation
- [ ] Added tests
- [ ] All tests pass locally
- [ ] No merge conflicts

---

## Community Guidelines

### Be Respectful
- Treat everyone with respect
- Welcome newcomers
- Be patient with questions
- Provide constructive feedback

### Be Collaborative
- Share knowledge
- Help others
- Acknowledge contributions
- Give credit where due

### Be Professional
- Keep discussions on-topic
- Avoid inflammatory language
- Focus on facts and code
- Assume good intentions

---

## Questions?

- **General Questions:** Open a [Discussion](https://github.com/ProfRandom92/comptext-codex/discussions)
- **Bug Reports:** Open an [Issue](https://github.com/ProfRandom92/comptext-codex/issues)
- **Security Issues:** Email [security contact]

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to CompText-Codex! 🙏**
