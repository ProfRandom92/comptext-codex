"""Public package interface for CompText-Codex."""

from importlib import resources

from .catalog import load_catalog
from .parser import CompTextParser, CommandInvocation
from .registry import CommandMetadata, CommandRegistry

__all__ = [
    "CompTextParser",
    "CommandInvocation",
    "CommandMetadata",
    "CommandRegistry",
    "load_catalog",
]

try:
    # Prefer the version declared in the package metadata when available.
    with resources.as_file(resources.files(__package__).joinpath(".VERSION")) as version_file:
        __version__ = version_file.read_text().strip()
except Exception:  # pragma: no cover - fallback for editable installs without metadata file
    __version__ = "0.0.0"
