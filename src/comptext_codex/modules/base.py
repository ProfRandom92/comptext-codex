"""Base module class for CompText modules.

Modules may optionally inherit from BaseModule (not required with the
decorator system), but it provides a convenient ``execute`` dispatcher.
"""

from abc import ABC
from typing import Any, Dict, List


class BaseModule(ABC):
    """Base class for all CompText modules.

    With the new ``@codex_module`` / ``@codex_command`` decorator system,
    subclassing BaseModule is optional.  The class is kept for backward
    compatibility and because the generic ``execute`` dispatcher is useful.
    """

    def get_commands(self) -> List[Dict[str, Any]]:
        """Return command metadata from the registry decorators."""
        from comptext_codex.registry import registry

        meta = getattr(self.__class__, "_module_meta", None)
        if meta is None:
            return []
        return [c.to_dict() for c in registry.get_commands_for_module(meta.code)]

    def execute(self, cmd, context: Dict[str, Any]) -> Any:
        handler_name = f"execute_{cmd.command.lower()}"
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            return handler(*cmd.args, context=context, **cmd.kwargs)
        raise NotImplementedError(f"Command {cmd.command} not implemented in {self.__class__.__name__}")
