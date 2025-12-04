"""General-purpose CompText commands."""
from __future__ import annotations

import re
from typing import Dict

from ..parser import Command


def _summarize_text(text: str, length: str = "short") -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip()) if text else []
    if not sentences:
        return "No text provided for summarization."

    target = 2 if length == "short" else min(len(sentences), 5)
    summary = " ".join(sentences[:target])
    return f"Summary ({length}): {summary}"


def summarize(command: Command, context: Dict[str, object]) -> str:
    text = context.get("text") or command.parameters.get("text") or ""
    length = command.parameters.get("length") or command.parameters.get("len") or "short"
    return _summarize_text(text, str(length))


def translate(command: Command, context: Dict[str, object]) -> str:
    target_lang = str(command.parameters.get("target_lang") or command.parameters.get("lang") or "english").title()
    style = command.parameters.get("style", "neutral")
    source = context.get("text") or command.parameters.get("text") or ""
    if not source:
        return "Nothing to translate. Provide `text` in the context or command parameters."
    return f"Translation to {target_lang} ({style} style): {source}"


def extract(command: Command, context: Dict[str, object]) -> str:
    pattern = command.parameters.get("pattern", "")
    text = context.get("text") or command.parameters.get("text") or ""
    if not pattern:
        return "No extraction pattern provided. Use pattern=email/urls or supply a regex."
    if pattern == "emails":
        regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    elif pattern == "urls":
        regex = r"https?://[^\s]+"
    else:
        regex = pattern
    matches = re.findall(regex, text)
    return f"Extracted {len(matches)} item(s): {matches}" if matches else "No matches found."


GENERAL_COMMANDS = {
    "SUMMARIZE": summarize,
    "TRANSLATE": translate,
    "EXTRACT": extract,
}

__all__ = ["GENERAL_COMMANDS"]
