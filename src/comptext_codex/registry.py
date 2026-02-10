"""Module & command registry with decorator-based auto-registration.

Instead of maintaining separate YAML files and manually wiring modules,
every module class uses ``@codex_module`` and every handler uses
``@codex_command`` to self-register at import time.

Usage::

    from comptext_codex.registry import codex_module, codex_command

    @codex_module(code="A", name="Core Commands",
                  purpose="Essential text manipulation commands")
    class ModuleA:
        @codex_command(syntax="@A:compress <text>",
                       description="Compress text by removing redundancy",
                       aliases=["shrink", "condense"],
                       token_cost_hint=50)
        def execute_compress(self, text, *, context=None, **kw):
            ...
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CommandMeta:
    """Metadata attached to a single command handler."""
    command: str  # derived from method name (execute_<command>)
    module: str = ""  # filled in by @codex_module
    syntax: str = ""
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    token_cost_hint: int = 0
    mcp_exposed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "command": self.command,
            "syntax": self.syntax,
            "description": self.description,
            "aliases": self.aliases,
            "examples": self.examples,
            "token_cost_hint": self.token_cost_hint,
            "mcp_exposed": self.mcp_exposed,
        }


@dataclass
class ModuleMeta:
    """Metadata attached to a module class."""
    code: str
    name: str
    purpose: str = ""
    token_priority: str = "medium"
    mcp_exposed: bool = True
    security: Dict[str, Any] = field(default_factory=dict)
    privacy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "purpose": self.purpose,
            "token_priority": self.token_priority,
            "mcp_exposed": self.mcp_exposed,
            "security": self.security,
            "privacy": self.privacy,
        }


# ---------------------------------------------------------------------------
# Global registry (populated at import time)
# ---------------------------------------------------------------------------

class ModuleRegistry:
    """Central registry holding all discovered module classes and their commands."""

    def __init__(self):
        self._modules: Dict[str, Type] = {}  # code -> class
        self._module_meta: Dict[str, ModuleMeta] = {}
        self._instances: Dict[str, Any] = {}  # lazy singleton per code

    def register_module(self, cls: Type, meta: ModuleMeta) -> None:
        self._modules[meta.code] = cls
        self._module_meta[meta.code] = meta
        logger.debug("Registered module %s (%s)", meta.code, meta.name)

    def get_instance(self, code: str) -> Optional[Any]:
        if code not in self._modules:
            return None
        if code not in self._instances:
            self._instances[code] = self._modules[code]()
        return self._instances[code]

    def list_module_codes(self) -> List[str]:
        return sorted(self._modules.keys())

    def get_module_meta(self, code: str) -> Optional[ModuleMeta]:
        return self._module_meta.get(code)

    def all_module_meta(self) -> List[ModuleMeta]:
        return [self._module_meta[c] for c in sorted(self._module_meta)]

    def all_command_meta(self) -> List[CommandMeta]:
        """Collect CommandMeta from all registered modules."""
        result: List[CommandMeta] = []
        for code in sorted(self._modules):
            cls = self._modules[code]
            for attr in dir(cls):
                fn = getattr(cls, attr, None)
                cm: Optional[CommandMeta] = getattr(fn, "_command_meta", None)
                if cm is not None:
                    result.append(cm)
        return result

    def get_commands_for_module(self, code: str) -> List[CommandMeta]:
        cls = self._modules.get(code)
        if cls is None:
            return []
        result: List[CommandMeta] = []
        for attr in dir(cls):
            fn = getattr(cls, attr, None)
            cm: Optional[CommandMeta] = getattr(fn, "_command_meta", None)
            if cm is not None and cm.module == code:
                result.append(cm)
        return result

    def clear(self):
        """Reset for testing."""
        self._modules.clear()
        self._module_meta.clear()
        self._instances.clear()


# Singleton instance
registry = ModuleRegistry()


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def codex_module(
    code: str,
    name: str,
    purpose: str = "",
    token_priority: str = "medium",
    mcp_exposed: bool = True,
    security: Optional[Dict[str, Any]] = None,
    privacy: Optional[Dict[str, Any]] = None,
):
    """Class decorator that registers a module in the global registry.

    Also walks the class body and stamps ``module=code`` on every
    ``@codex_command``-decorated method.
    """
    def decorator(cls: Type) -> Type:
        meta = ModuleMeta(
            code=code,
            name=name,
            purpose=purpose,
            token_priority=token_priority,
            mcp_exposed=mcp_exposed,
            security=security or {},
            privacy=privacy or {},
        )
        cls._module_meta = meta  # type: ignore[attr-defined]

        # Patch module code into every command handler defined on this class
        for attr_name in list(vars(cls)):
            fn = getattr(cls, attr_name, None)
            cm: Optional[CommandMeta] = getattr(fn, "_command_meta", None)
            if cm is not None:
                cm.module = code

        registry.register_module(cls, meta)
        return cls

    return decorator


def codex_command(
    syntax: str = "",
    description: str = "",
    aliases: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    token_cost_hint: int = 0,
    mcp_exposed: bool = True,
):
    """Method decorator that attaches command metadata to ``execute_*`` methods.

    The *command* name is derived from the method name by stripping the
    ``execute_`` prefix.
    """
    def decorator(fn: Callable) -> Callable:
        name = fn.__name__
        if name.startswith("execute_"):
            cmd_name = name[8:]  # strip "execute_"
        else:
            cmd_name = name

        fn._command_meta = CommandMeta(  # type: ignore[attr-defined]
            command=cmd_name,
            syntax=syntax,
            description=description,
            aliases=aliases or [],
            examples=examples or [],
            token_cost_hint=token_cost_hint,
            mcp_exposed=mcp_exposed,
        )
        return fn

    return decorator


def ensure_modules_loaded() -> None:
    """Import all module files so decorators run and modules register."""
    import importlib

    for letter in "abcdefghijklmn":
        try:
            importlib.import_module(f"comptext_codex.modules.module_{letter}")
        except ImportError:
            pass
