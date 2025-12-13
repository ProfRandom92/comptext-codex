"""
CompText Codex Bundle Loader (Reference)

- Loads codex.bundle.json from:
  1) local path
  2) HTTPS URL (e.g., GitHub Release asset)
- Supports ETag caching to disk
- Provides deterministic retrieval:
  - get_command(name_or_alias)
  - get_module(code)
  - search(query, filters)
  - expand(ids, token_budget)

NOTE: Token budgeting here is approximate: based on character count.
Replace with your tokenizer if needed.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Literal

try:
    import requests
except Exception as e:
    raise RuntimeError("requests is required: pip install requests") from e

Kind = Literal["module","command","profile"]

@dataclass(frozen=True)
class SearchFilters:
    kind: Optional[Kind] = None
    module_code: Optional[str] = None
    stability: Optional[str] = "stable"   # default: stable/frozen only
    mcp_exposed: Optional[bool] = True

class CodexBundle:
    def __init__(self, bundle: Dict[str, Any]):
        self.bundle = bundle
        self.meta = bundle["meta"]
        self.modules = {m["id"]: m for m in bundle["modules"]}
        self.commands = {c["id"]: c for c in bundle["commands"]}
        self.profiles = {p["id"]: p for p in bundle["profiles"]}
        self.indexes = bundle["indexes"]

        # Reverse helpers
        self.module_by_code = self.indexes["by_module_code"]
        self.command_by_name = self.indexes["by_command_name"]
        self.command_by_alias = self.indexes["by_alias"]

        # Search index list
        self.search_rows = self.indexes["search"]

    def get_module(self, code: str) -> Dict[str, Any]:
        code = code.strip().upper()
        mid = self.module_by_code.get(code)
        if not mid:
            raise KeyError(f"Unknown module code: {code}")
        return self.modules[mid]

    def get_command(self, name_or_alias: str) -> Dict[str, Any]:
        key = name_or_alias.strip()
        key_up = key.upper()
        cid = self.command_by_name.get(key_up) or self.command_by_alias.get(key_up)
        if not cid:
            # fall back: accept "cmd:XYZ"
            if key.startswith("cmd:"):
                cid = key
        if not cid or cid not in self.commands:
            raise KeyError(f"Unknown command: {name_or_alias}")
        return self.commands[cid]

    def search(self, query: str, filters: SearchFilters = SearchFilters(), limit: int = 10) -> List[Dict[str, Any]]:
        q = query.strip().lower()
        terms = [t for t in re.split(r"[^a-z0-9_:+-]+", q) if t]
        if not terms:
            return []

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for row in self.search_rows:
            if filters.kind and row["kind"] != filters.kind:
                continue
            if filters.module_code and row.get("module_code") != filters.module_code:
                continue
            if filters.mcp_exposed is not None and row.get("mcp_exposed") != filters.mcp_exposed:
                continue
            if filters.stability:
                # allow frozen as stable for retrieval
                if row.get("stability") not in {filters.stability, "frozen"}:
                    continue

            text = (row.get("text_compact") or "").lower()
            kws = [k.lower() for k in (row.get("keywords") or [])]
            score = 0.0
            for t in terms:
                if t in kws:
                    score += 3.0
                if t in text:
                    score += 1.0
                if row["id"].lower().endswith(t):
                    score += 2.0
            if score > 0:
                scored.append((score, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:limit]]

    def expand(self, ids: Iterable[str], token_budget: int = 1200) -> str:
        """
        Assemble LLM context in a deterministic compact format.
        token_budget is approximate; uses ~4 chars/token heuristic.
        """
        max_chars = max(200, token_budget * 4)
        parts: List[str] = []
        used = 0

        def add(block: str):
            nonlocal used
            if not block:
                return
            b = block.strip() + "\n"
            if used + len(b) > max_chars:
                return
            parts.append(b)
            used += len(b)

        for _id in ids:
            obj = self.modules.get(_id) or self.commands.get(_id) or self.profiles.get(_id)
            if not obj:
                continue

            if _id.startswith("cmd:"):
                add(_format_command(obj, self._module_code_for(obj.get("module_id"))))
            elif _id.startswith("module:"):
                add(_format_module(obj))
            elif _id.startswith("profile:"):
                add(_format_profile(obj))
        return "\n".join(parts).strip()

    def _module_code_for(self, module_id: Optional[str]) -> str:
        if not module_id:
            return "?"
        m = self.modules.get(module_id)
        return m.get("code") if m else "?"

def _format_command(c: Dict[str, Any], module_code: str) -> str:
    return (
        f"[COMMAND] {c['name']} (Module {module_code}, {c['stability']})\n"
        f"Syntax: {c['syntax']}\n"
        f"Description: {c['description']}\n"
        + (f"Example: {c['examples'][0]}\n" if c.get("examples") else "")
        + (f"Aliases: {', '.join(c.get('aliases') or [])}\n" if c.get("aliases") else "")
    ).strip()

def _format_module(m: Dict[str, Any]) -> str:
    return (
        f"[MODULE] {m['code']} — {m['name']} ({m['stability']})\n"
        f"Purpose: {m['purpose']}\n"
        f"Commands: {', '.join(m.get('command_ids') or [])}\n"
    ).strip()

def _format_profile(p: Dict[str, Any]) -> str:
    rules = p.get("rules") or []
    rules_preview = "; ".join(rules[:3]) + ("; …" if len(rules) > 3 else "")
    return (
        f"[PROFILE] {p['name']} ({p['type']}, {p['stability']})\n"
        f"Rules: {rules_preview}\n"
    ).strip()

def _http_get(url: str, cache_dir: Path) -> Dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    etag_path = cache_dir / "etag.txt"
    json_path = cache_dir / "codex.bundle.json"

    headers = {}
    if etag_path.exists():
        headers["If-None-Match"] = etag_path.read_text(encoding="utf-8").strip()

    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 304 and json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))

    resp.raise_for_status()
    etag = resp.headers.get("ETag")
    if etag:
        etag_path.write_text(etag, encoding="utf-8")
    json_path.write_text(resp.text, encoding="utf-8")
    return resp.json()

def load_bundle(source: str, cache_dir: Optional[str] = ".cache/comptext") -> CodexBundle:
    """
    source can be:
      - local file path to codex.bundle.json
      - https:// URL to codex.bundle.json (GitHub Release asset)
    """
    if source.startswith("http://") or source.startswith("https://"):
        cache = Path(cache_dir or ".cache/comptext")
        bundle = _http_get(source, cache)
        return CodexBundle(bundle)

    p = Path(source)
    bundle = json.loads(p.read_text(encoding="utf-8"))
    return CodexBundle(bundle)
