"""CodexStore - SQLite-based data layer replacing YAML/Notion flat files.

Provides a single-file, zero-config, queryable data store for all codex
definitions: modules, commands, profiles, and catalog entries.  Uses WAL
mode for concurrent readers.
"""

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional


_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "codex.db"


class CodexStore:
    """Embedded SQLite store for CompText Codex data."""

    def __init__(self, db_path: Optional[str] = None):
        self._db_path = str(db_path or _DEFAULT_DB_PATH)
        self._local = threading.local()
        self._ensure_schema()

    # -- connection management ------------------------------------------------

    @property
    def _conn(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn = conn
        return conn

    @contextmanager
    def _cursor(self):
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    def close(self):
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    # -- schema ---------------------------------------------------------------

    def _ensure_schema(self):
        with self._cursor() as cur:
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS modules (
                    code        TEXT PRIMARY KEY,
                    name        TEXT NOT NULL,
                    purpose     TEXT NOT NULL DEFAULT '',
                    token_priority TEXT NOT NULL DEFAULT 'medium',
                    mcp_exposed INTEGER NOT NULL DEFAULT 1,
                    security    TEXT NOT NULL DEFAULT '{}',
                    privacy     TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS commands (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    module      TEXT NOT NULL REFERENCES modules(code),
                    command     TEXT NOT NULL,
                    syntax      TEXT NOT NULL DEFAULT '',
                    description TEXT NOT NULL DEFAULT '',
                    examples    TEXT NOT NULL DEFAULT '[]',
                    aliases     TEXT NOT NULL DEFAULT '[]',
                    token_cost_hint INTEGER NOT NULL DEFAULT 0,
                    mcp_exposed INTEGER NOT NULL DEFAULT 1,
                    UNIQUE(module, command)
                );

                CREATE TABLE IF NOT EXISTS profiles (
                    name            TEXT PRIMARY KEY,
                    description     TEXT NOT NULL DEFAULT '',
                    enabled_modules TEXT NOT NULL DEFAULT '[]',
                    default_settings TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS catalog (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    module_ref  TEXT NOT NULL DEFAULT '',
                    tags        TEXT NOT NULL DEFAULT '[]',
                    entry_type  TEXT NOT NULL DEFAULT 'documentation'
                );

                CREATE INDEX IF NOT EXISTS idx_commands_module ON commands(module);
                CREATE INDEX IF NOT EXISTS idx_catalog_module ON catalog(module_ref);
                CREATE INDEX IF NOT EXISTS idx_catalog_type ON catalog(entry_type);
            """)

    # -- module CRUD ----------------------------------------------------------

    def upsert_module(self, module: Dict[str, Any]) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO modules (code, name, purpose, token_priority,
                                        mcp_exposed, security, privacy)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(code) DO UPDATE SET
                       name=excluded.name,
                       purpose=excluded.purpose,
                       token_priority=excluded.token_priority,
                       mcp_exposed=excluded.mcp_exposed,
                       security=excluded.security,
                       privacy=excluded.privacy""",
                (
                    module["code"],
                    module["name"],
                    module.get("purpose", ""),
                    module.get("token_priority", "medium"),
                    1 if module.get("mcp_exposed", True) else 0,
                    json.dumps(module.get("security", {})),
                    json.dumps(module.get("privacy", {})),
                ),
            )

    def get_module(self, code: str) -> Optional[Dict[str, Any]]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM modules WHERE code = ?", (code,))
            row = cur.fetchone()
            return self._row_to_module(row) if row else None

    def list_modules(self) -> List[Dict[str, Any]]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM modules ORDER BY code")
            return [self._row_to_module(r) for r in cur.fetchall()]

    @staticmethod
    def _row_to_module(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "code": row["code"],
            "name": row["name"],
            "purpose": row["purpose"],
            "token_priority": row["token_priority"],
            "mcp_exposed": bool(row["mcp_exposed"]),
            "security": json.loads(row["security"]),
            "privacy": json.loads(row["privacy"]),
        }

    # -- command CRUD ---------------------------------------------------------

    def upsert_command(self, cmd: Dict[str, Any]) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO commands (module, command, syntax, description,
                                         examples, aliases, token_cost_hint,
                                         mcp_exposed)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(module, command) DO UPDATE SET
                       syntax=excluded.syntax,
                       description=excluded.description,
                       examples=excluded.examples,
                       aliases=excluded.aliases,
                       token_cost_hint=excluded.token_cost_hint,
                       mcp_exposed=excluded.mcp_exposed""",
                (
                    cmd["module"],
                    cmd["command"],
                    cmd.get("syntax", ""),
                    cmd.get("description", ""),
                    json.dumps(cmd.get("examples", [])),
                    json.dumps(cmd.get("aliases", [])),
                    cmd.get("token_cost_hint", 0),
                    1 if cmd.get("mcp_exposed", True) else 0,
                ),
            )

    def get_command(self, module: str, command: str) -> Optional[Dict[str, Any]]:
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM commands WHERE module = ? AND command = ?",
                (module, command),
            )
            row = cur.fetchone()
            return self._row_to_command(row) if row else None

    def list_commands(self, module: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._cursor() as cur:
            if module:
                cur.execute(
                    "SELECT * FROM commands WHERE module = ? ORDER BY command",
                    (module,),
                )
            else:
                cur.execute("SELECT * FROM commands ORDER BY module, command")
            return [self._row_to_command(r) for r in cur.fetchall()]

    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        with self._cursor() as cur:
            like = f"%{query}%"
            cur.execute(
                """SELECT * FROM commands
                   WHERE command LIKE ? OR description LIKE ? OR aliases LIKE ?
                   ORDER BY module, command""",
                (like, like, like),
            )
            return [self._row_to_command(r) for r in cur.fetchall()]

    @staticmethod
    def _row_to_command(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "module": row["module"],
            "command": row["command"],
            "syntax": row["syntax"],
            "description": row["description"],
            "examples": json.loads(row["examples"]),
            "aliases": json.loads(row["aliases"]),
            "token_cost_hint": row["token_cost_hint"],
            "mcp_exposed": bool(row["mcp_exposed"]),
        }

    # -- profile CRUD ---------------------------------------------------------

    def upsert_profile(self, profile: Dict[str, Any]) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO profiles (name, description, enabled_modules,
                                         default_settings)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                       description=excluded.description,
                       enabled_modules=excluded.enabled_modules,
                       default_settings=excluded.default_settings""",
                (
                    profile["name"],
                    profile.get("description", ""),
                    json.dumps(profile.get("enabled_modules", [])),
                    json.dumps(profile.get("default_settings", {})),
                ),
            )

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM profiles WHERE name = ?", (name,))
            row = cur.fetchone()
            return self._row_to_profile(row) if row else None

    def list_profiles(self) -> List[Dict[str, Any]]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM profiles ORDER BY name")
            return [self._row_to_profile(r) for r in cur.fetchall()]

    @staticmethod
    def _row_to_profile(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "name": row["name"],
            "description": row["description"],
            "enabled_modules": json.loads(row["enabled_modules"]),
            "default_settings": json.loads(row["default_settings"]),
        }

    # -- catalog CRUD ---------------------------------------------------------

    def add_catalog_entry(self, entry: Dict[str, Any]) -> int:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO catalog (title, description, module_ref, tags,
                                        entry_type)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    entry["title"],
                    entry.get("description", ""),
                    entry.get("module_ref", ""),
                    json.dumps(entry.get("tags", [])),
                    entry.get("entry_type", "documentation"),
                ),
            )
            return cur.lastrowid

    def list_catalog(
        self,
        entry_type: Optional[str] = None,
        module_ref: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self._cursor() as cur:
            conditions, params = [], []
            if entry_type:
                conditions.append("entry_type = ?")
                params.append(entry_type)
            if module_ref:
                conditions.append("module_ref = ?")
                params.append(module_ref)
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cur.execute(
                f"SELECT * FROM catalog {where} ORDER BY id", params
            )
            return [self._row_to_catalog(r) for r in cur.fetchall()]

    def search_catalog(self, query: str) -> List[Dict[str, Any]]:
        with self._cursor() as cur:
            like = f"%{query}%"
            cur.execute(
                """SELECT * FROM catalog
                   WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
                   ORDER BY id""",
                (like, like, like),
            )
            return [self._row_to_catalog(r) for r in cur.fetchall()]

    @staticmethod
    def _row_to_catalog(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "module_ref": row["module_ref"],
            "tags": json.loads(row["tags"]),
            "entry_type": row["entry_type"],
        }

    # -- export / import ------------------------------------------------------

    def export_bundle(self) -> Dict[str, Any]:
        """Export entire store as a JSON-serialisable dict (replaces build_bundle.py)."""
        return {
            "modules": self.list_modules(),
            "commands": self.list_commands(),
            "profiles": self.list_profiles(),
            "catalog": self.list_catalog(),
        }

    def import_bundle(self, bundle: Dict[str, Any]) -> Dict[str, int]:
        """Import a bundle dict into the store (idempotent via upsert)."""
        counts = {"modules": 0, "commands": 0, "profiles": 0, "catalog": 0}
        for m in bundle.get("modules", []):
            self.upsert_module(m)
            counts["modules"] += 1
        for c in bundle.get("commands", []):
            self.upsert_command(c)
            counts["commands"] += 1
        for p in bundle.get("profiles", []):
            self.upsert_profile(p)
            counts["profiles"] += 1
        for e in bundle.get("catalog", []):
            self.add_catalog_entry(e)
            counts["catalog"] += 1
        return counts

    # -- statistics -----------------------------------------------------------

    def stats(self) -> Dict[str, int]:
        with self._cursor() as cur:
            result = {}
            for table in ("modules", "commands", "profiles", "catalog"):
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                result[table] = cur.fetchone()[0]
            return result
