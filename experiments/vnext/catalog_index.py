"""Disposable SQLite FTS5 projection from a validated immutable Codex catalog.

The Git-versioned JSON catalog is the input. This SQLite file is
rebuildable, never treated as authority, and contains NO executable tools.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sqlite3
from urllib.parse import quote
from uuid import uuid4

from .catalog import load_catalog, _key


class CatalogIndexError(ValueError):
    """Invalid or unsafe derived search index."""


HEX = re.compile(r"^[0-9a-f]{64}$")
SEARCH_TERMS = re.compile(r"[\wÀ-ÿ]{2,}",re.UNICODE)


def build_search_index(catalog_path: str | Path, output_path: str | Path) -> dict:
    catalog = load_catalog(catalog_path)
    output = Path(output_path)
    if output.exists():
        raise CatalogIndexError("search index exists; refusing overwrite")
    output.parent.mkdir(parents=True,exist_ok=True)
    temp = output.with_name("." + output.name + "." + uuid4().hex + ".tmp")
    fd = os.open(temp,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    os.close(fd)
    try:
        con=sqlite3.connect(str(temp))
        try:
            con.execute("pragma journal_mode=DELETE")
            con.executescript("""
                CREATE TABLE metadata(k TEXT PRIMARY KEY, v TEXT NOT NULL);
                CREATE TABLE commands (
                    id INTEGER PRIMARY KEY,
                    module TEXT NOT NULL,
                    command TEXT NOT NULL,
                    semantic_key TEXT NOT NULL,
                    syntax TEXT NOT NULL,
                    description TEXT NOT NULL,
                    quality TEXT NOT NULL,
                    issues TEXT NOT NULL,
                    yaml_matches INTEGER NOT NULL,
                    can_execute INTEGER NOT NULL CHECK(can_execute=0)
                );
                CREATE INDEX commands_identity ON commands(semantic_key);
                CREATE VIRTUAL TABLE command_search USING fts5(
                    command,description,syntax,
                    tokenize='unicode61'
                );
            """)
            con.executemany("INSERT INTO metadata VALUES (?,?)",[
                ("catalog_sha256",catalog["sha256"]),
                ("catalog_schema",catalog["schema"])
            ])
            for item in catalog["commands"]:
                con.execute(
                    "INSERT INTO commands VALUES (?,?,?,?,?,?,?,?,?,0)",
                    (
                        item["legacy_id"],item["module"],item["command"],
                        item["semantic_key"],item["syntax"],item["description"],
                        item["quality"],json.dumps(item["issues"]),
                        len(item["yaml_provenance"])
                    ),
                )
                con.execute(
                    "INSERT INTO command_search(rowid,command,description,syntax) VALUES (?,?,?,?)",
                    (item["legacy_id"],item["command"],item["description"],item["syntax"]),
                )
            con.commit()
            if con.execute("pragma integrity_check").fetchone()[0]!="ok":
                raise CatalogIndexError("SQLite derived index integrity failure")
        finally:
            con.close()
        os.chmod(temp,0o600)
        if output.exists():
            raise CatalogIndexError("search index exists; refusing overwrite")
        # Atomic no-overwrite publish, preserving any already existing index.
        os.link(temp,output)
        return {"rows":len(catalog["commands"]),
                "catalog_sha256":catalog["sha256"],
                "output":str(output)}
    except (sqlite3.Error,OSError) as error:
        raise CatalogIndexError("failed to build derived SQLite index") from error
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def open_search_index(
    path: str | Path, *, expected_catalog_sha256: str | None
):
    if type(expected_catalog_sha256) is not str or not HEX.fullmatch(expected_catalog_sha256):
        raise CatalogIndexError("externally supplied expected digest required")
    file=Path(path)
    if not file.is_file() or file.is_symlink():
        raise CatalogIndexError("missing derived index")
    uri="file:"+quote(str(file.resolve()),safe="/")+"?mode=ro&immutable=1"
    con=None
    try:
        con=sqlite3.connect(uri,uri=True,timeout=3)
        con.row_factory=sqlite3.Row
        con.execute("pragma query_only=ON")
        actual=con.execute("SELECT v FROM metadata WHERE k='catalog_sha256'").fetchone()
        if not actual or actual[0]!=expected_catalog_sha256:
            raise CatalogIndexError("index digest mismatch")
        if con.execute("pragma integrity_check").fetchone()[0]!="ok":
            raise CatalogIndexError("index integrity failure")
        yield con
    except sqlite3.Error as error:
        raise CatalogIndexError("index unavailable") from error
    finally:
        if con is not None:
            con.close()


def _view(row: sqlite3.Row) -> dict:
    return {
        "legacy_id":row["id"],
        "module":row["module"],
        "command":row["command"],
        "syntax":row["syntax"],
        "description":row["description"],
        "quality":row["quality"],
        "yaml_matches":row["yaml_matches"],
        "can_execute":False,
    }


def lookup_catalog(
    con: sqlite3.Connection, *, module: str, command: str
) -> dict | None:
    if type(module) is not str or type(command) is not str or len(command)>128:
        return None
    key=_key(module.upper(),command)
    results=con.execute(
        "SELECT * FROM commands WHERE semantic_key=? AND quality='unreviewed' LIMIT 2",
        (key,),
    ).fetchall()
    return _view(results[0]) if len(results)==1 else None


def search_catalog(con: sqlite3.Connection, text: str, *, limit: int=10) -> list[dict]:
    if type(text) is not str or not 1<=len(text)<=256:
        return []
    if type(limit) is not int or not 1<=limit<=50:
        raise CatalogIndexError("invalid search limit")
    terms=SEARCH_TERMS.findall(text.casefold())[:6]
    if not terms:
        return []
    # Input is never interpolated into SQL. FTS operators are quoted per token.
    q=" ".join('"' + term.replace('"','') + '"' for term in terms)
    try:
        rows=con.execute(
            "SELECT c.* FROM command_search f JOIN commands c ON c.id=f.rowid "
            "WHERE command_search MATCH ? AND c.quality='unreviewed' "
            "ORDER BY bm25(command_search) LIMIT ?",
            (q,limit),
        ).fetchall()
    except sqlite3.Error as error:
        raise CatalogIndexError("FTS query unavailable") from error
    return [_view(row) for row in rows]
