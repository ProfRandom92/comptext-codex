"""Base module class for CompText modules."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseModule(ABC):
    """Base class for all CompText modules."""

    def __init__(self):
        """Initialize module."""
        self.name = self.__class__.__name__
        self.code = self.name[-1]  # Extract module code (A-M)

    @abstractmethod
    def get_commands(self) -> List[Dict[str, Any]]:
        """Return list of available commands in this module."""
        pass

    def execute(self, cmd, context: Dict[str, Any]) -> Any:
        """Generic execute method for commands.

        Args:
            cmd: CompTextCommand object
            context: Execution context

        Returns:
            Command execution result
        """
        handler_name = f"execute_{cmd.command.lower()}"
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            return handler(*cmd.args, context=context, **cmd.kwargs)

        raise NotImplementedError(f"Command {cmd.command} not implemented in {self.name}")
