"""CompText DSL Executor - Executes parsed CompText commands."""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import logging
import warnings

from .parser import CompTextCommand, CompTextParser
from .exceptions import (
    ExecutionError,
    ModuleNotFoundError_,
    CommandNotFoundError,
    HandlerError,
)

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CompTextExecutor:
    """Executes CompText commands by dispatching to appropriate modules."""

    def __init__(self, codex_dir: Optional[str] = None):
        """Initialize executor.

        Args:
            codex_dir: Path to codex directory for loading definitions (legacy)
        """
        self.codex_dir = codex_dir
        self.parser = CompTextParser(codex_dir=codex_dir)
        self._module_instances: Dict[str, Any] = {}
        self._command_handlers: Dict[str, Callable] = {}
        self._registry = None
        self._load_modules()

    def _load_modules(self):
        """Load modules via the auto-registration registry."""
        try:
            from .registry import ensure_modules_loaded, registry
            ensure_modules_loaded()
            self._registry = registry
            # Pre-populate instances for all registered modules
            for code in registry.list_module_codes():
                self._module_instances[code] = registry.get_instance(code)
            logger.debug("Loaded %d modules from registry", len(self._module_instances))
        except ImportError as e:
            logger.warning("Failed to load registry, falling back to legacy: %s", e)
            self._load_modules_legacy()

    def _load_modules_legacy(self):
        """Fallback: Dynamically load module implementations via importlib."""
        warnings.warn(
            "Legacy module loading via importlib is deprecated. "
            "Ensure the registry module is importable.",
            DeprecationWarning,
            stacklevel=2,
        )
        import importlib
        for code in "ABCDEFGHIJKLMN":
            try:
                module_name = f"comptext_codex.modules.module_{code.lower()}"
                module = importlib.import_module(module_name)
                if hasattr(module, "get_module"):
                    self._module_instances[code] = module.get_module()
                else:
                    self._module_instances[code] = module
            except ImportError as e:
                logger.debug("Module %s not implemented: %s", code, e)
                self._module_instances[code] = None

    def execute(self, command_string: str, context: Optional[Dict[str, Any]] = None) -> List[ExecutionResult]:
        """Execute CompText command(s).

        Args:
            command_string: Raw CompText command(s)
            context: Optional execution context with variables

        Returns:
            List of execution results for each command

        Examples:
            >>> executor = CompTextExecutor()
            >>> results = executor.execute("@A:compress The quick brown fox")
            >>> print(results[0].result)
        """
        context = context or {}

        # Parse commands
        commands = self.parser.parse(command_string)

        if not commands:
            return [ExecutionResult(
                success=False,
                result=None,
                error="Failed to parse command"
            )]

        # Execute each command in sequence
        results = []
        execution_context = context.copy()

        for cmd in commands:
            result = self._execute_single(cmd, execution_context)
            results.append(result)

            # Update context with result for chained commands
            if result.success:
                execution_context['_last_result'] = result.result

        return results

    def _execute_single(self, cmd: CompTextCommand, context: Dict[str, Any]) -> ExecutionResult:
        """Execute a single command.

        Args:
            cmd: Parsed command
            context: Execution context

        Returns:
            Execution result
        """
        try:
            # Get module instance (from registry or legacy)
            module = self._module_instances.get(cmd.module)

            if module is None:
                return self._execute_fallback(cmd, context)

            # Find command handler
            handler_name = f"execute_{cmd.command.lower()}"

            if hasattr(module, handler_name):
                handler = getattr(module, handler_name)
                result = handler(*cmd.args, context=context, **cmd.kwargs)

                return ExecutionResult(
                    success=True,
                    result=result,
                    metadata={
                        'module': cmd.module,
                        'command': cmd.command
                    }
                )
            elif hasattr(module, 'execute'):
                # Generic execute method
                try:
                    result = module.execute(cmd, context)
                    return ExecutionResult(
                        success=True,
                        result=result,
                        metadata={
                            'module': cmd.module,
                            'command': cmd.command
                        }
                    )
                except NotImplementedError:
                    return self._execute_fallback(cmd, context)
            else:
                return self._execute_fallback(cmd, context)

        except Exception as e:
            wrapped = HandlerError(
                f"Error executing {cmd.module}:{cmd.command}: {e}"
            )
            wrapped.__cause__ = e
            logger.error(str(wrapped))
            return ExecutionResult(
                success=False,
                result=None,
                error=str(wrapped),
                metadata={
                    'module': cmd.module,
                    'command': cmd.command,
                    'exception_type': type(e).__name__,
                }
            )

    def _execute_fallback(self, cmd: CompTextCommand, context: Dict[str, Any]) -> ExecutionResult:
        """Fallback execution for unimplemented commands.

        Returns a mock result that describes what would be executed.
        """
        return ExecutionResult(
            success=True,
            result={
                'status': 'simulated',
                'message': f"Command {cmd.module}:{cmd.command} would execute with args={cmd.args}, kwargs={cmd.kwargs}",
                'module': cmd.module,
                'command': cmd.command,
                'args': cmd.args,
                'kwargs': cmd.kwargs
            },
            metadata={
                'simulated': True,
                'module': cmd.module,
                'command': cmd.command
            }
        )

    def register_handler(self, module: str, command: str, handler: Callable):
        """Register a custom command handler.

        Args:
            module: Module code (A-M)
            command: Command name
            handler: Callable that executes the command
        """
        key = f"{module}:{command}"
        self._command_handlers[key] = handler

    def get_available_commands(self) -> List[Dict[str, Any]]:
        """Get list of available commands.

        Returns:
            List of command metadata dictionaries
        """
        # Prefer registry metadata (includes descriptions, aliases, etc.)
        if self._registry is not None:
            return [cmd.to_dict() for cmd in self._registry.all_command_meta()]

        # Fallback: introspect module instances
        commands = []
        for module_code, module in self._module_instances.items():
            if module is None:
                continue
            if hasattr(module, "get_commands"):
                commands.extend(module.get_commands())
            else:
                for attr_name in dir(module):
                    if attr_name.startswith("execute_"):
                        command_name = attr_name[8:]
                        commands.append({
                            "module": module_code,
                            "command": command_name,
                            "syntax": f"@{module_code}:{command_name}",
                        })
        return commands


# Convenience function
def execute(command_string: str, context: Optional[Dict[str, Any]] = None,
            codex_dir: Optional[str] = None) -> List[ExecutionResult]:
    """Execute CompText command(s).

    Args:
        command_string: Raw CompText command(s)
        context: Optional execution context
        codex_dir: Optional path to codex directory

    Returns:
        List of execution results
    """
    executor = CompTextExecutor(codex_dir=codex_dir)
    return executor.execute(command_string, context=context)
