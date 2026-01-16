# Parser API Reference

## CompTextParser

The main parser class for CompText DSL commands.

### Class: `CompTextParser`

```python
from comptext_codex.parser import CompTextParser

parser = CompTextParser(codex_dir=None)
```

#### Parameters

- **codex_dir** (str, optional): Path to codex directory for loading command definitions

### Methods

#### `parse(command_string: str) -> List[CompTextCommand]`

Parse a CompText command string into structured commands.

**Parameters:**
- `command_string` (str): Raw CompText command(s)

**Returns:**
- List of `CompTextCommand` objects

**Example:**
```python
commands = parser.parse("@A:compress The quick brown fox")
print(commands[0].module)  # 'A'
print(commands[0].command)  # 'compress'
print(commands[0].args)     # ['The quick brown fox']
```

#### `validate(commands: List[CompTextCommand]) -> Tuple[bool, List[str]]`

Validate parsed commands against registry.

**Returns:**
- Tuple of (is_valid, error_messages)

### CompTextCommand

Dataclass representing a parsed command.

**Attributes:**
- `module` (str): Module code (A-M)
- `command` (str): Command name
- `args` (List[str]): Positional arguments
- `kwargs` (Dict[str, Any]): Keyword arguments
- `raw` (str): Original command string

### Supported Syntax Patterns

#### 1. Simple Format
```
@A:compress <text>
@B:analyze <content>
```

#### 2. Parametric Format
```
@CODE_ANALYZE[perf_bottleneck, complexity]
@AUTOML[task=classification, metric=f1]
```

#### 3. Chained Commands
```
@EXTRACT[source=db] + @TRANSFORM[clean=true] + @LOAD[dest=warehouse]
```

### Convenience Function

```python
from comptext_codex.parser import parse

commands = parse("@A:compress text")
```
