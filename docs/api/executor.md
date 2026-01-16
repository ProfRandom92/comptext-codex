# Executor API Reference

## CompTextExecutor

Executes parsed CompText commands by dispatching to appropriate modules.

### Class: `CompTextExecutor`

```python
from comptext_codex.executor import CompTextExecutor

executor = CompTextExecutor(codex_dir=None)
```

#### Parameters

- **codex_dir** (str, optional): Path to codex directory

### Methods

#### `execute(command_string: str, context: Dict[str, Any] = None) -> List[ExecutionResult]`

Execute CompText command(s).

**Parameters:**
- `command_string` (str): Raw CompText command(s)
- `context` (dict, optional): Execution context with variables

**Returns:**
- List of `ExecutionResult` objects

**Example:**
```python
results = executor.execute("@A:compress The quick brown fox")
if results[0].success:
    print(results[0].result)
```

#### `get_available_commands() -> List[Dict[str, Any]]`

Get list of available commands.

**Returns:**
- List of command metadata dictionaries

**Example:**
```python
commands = executor.get_available_commands()
for cmd in commands:
    print(f"{cmd['module']}:{cmd['command']}")
```

#### `register_handler(module: str, command: str, handler: Callable)`

Register a custom command handler.

**Parameters:**
- `module` (str): Module code (A-M)
- `command` (str): Command name
- `handler` (Callable): Function to handle command

### ExecutionResult

Dataclass representing command execution result.

**Attributes:**
- `success` (bool): Whether execution succeeded
- `result` (Any): Command result
- `error` (str, optional): Error message if failed
- `metadata` (dict): Execution metadata

### Context Variables

Context is a dictionary that can contain:
- **code**: Source code for analysis
- **dataset**: Data for ML pipelines
- **path**: File path for operations
- **_last_result**: Result from previous command (for chains)

### Error Handling

```python
results = executor.execute("@INVALID_COMMAND")
if not results[0].success:
    print(f"Error: {results[0].error}")
```

### Convenience Function

```python
from comptext_codex.executor import execute

results = execute("@A:compress text", context={'key': 'value'})
```
