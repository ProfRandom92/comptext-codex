"""TDD contracts: deterministic, provenance-preserving Codex catalog rebuild.

No Notion API, no command execution, no implicit human validation.
"""
import hashlib
import json
import sqlite3
from pathlib import Path
import pytest
import yaml

from experiments.vnext.catalog import (
    build_catalog, verify_catalog, save_catalog, load_catalog, CatalogError,
    command_lookup
)

def fixture(tmp_path):
    p=tmp_path/"old.db"
    c=sqlite3.connect(p)
    c.executescript("""
        CREATE TABLE modules(code TEXT PRIMARY KEY,name TEXT);
        CREATE TABLE commands(id INTEGER PRIMARY KEY,module TEXT,command TEXT,
            syntax TEXT,description TEXT,examples TEXT,aliases TEXT,
            token_cost_hint INTEGER,mcp_exposed INTEGER);
        CREATE TABLE profiles(name TEXT PRIMARY KEY);
        CREATE TABLE catalog(id INTEGER PRIMARY KEY,title TEXT);
    """)
    c.executemany("INSERT INTO modules VALUES (?,?)",[("A","Core"),("J","DevOps")])
    c.executemany("INSERT INTO commands VALUES (?,?,?,?,?,?,?,?,?)",[
        (1,"A","@sum","@sum <text>","Summarize provided text","[]","[]",50,1),
        (2,"J","deploy","CMD:DEPLOY","Release preview only","[]","[]",5,1),
        (3,"J","DEPLOY","CMD:DEPLOY","Command (auto-extracted)","[]","[]",5,1)
    ])
    c.execute("INSERT INTO profiles VALUES ('default')")
    c.execute("INSERT INTO catalog VALUES (1,'historical Notion catalogue item')")
    c.commit();c.close()
    source=tmp_path/"yaml";source.mkdir()
    (source/"deploy.yaml").write_text(yaml.safe_dump({
        "id":"cmd:DEPLOY", "name":"DEPLOY","module_id":"module:J",
        "syntax":"CMD:DEPLOY","description":"Only explicit deployment",
        "stability":"experimental","aliases":["DEPLOY"],
        "examples":["CMD:DEPLOY;ENV:DEV"],"mcp_exposed":True
    }),encoding="utf8")
    return p,source


def test_rebuild_preserves_every_historic_row_and_quarantines_ambiguous_commands(tmp_path):
    db,yamls=fixture(tmp_path)
    report=build_catalog(db,yamls)
    assert report["schema"]=="comptext.codex.catalog.v1"
    assert report["stats"]["legacy_rows"]==3
    assert report["stats"]["yaml_entries"]==1
    assert report["stats"]["yaml_matches"]==1
    assert report["stats"]["legacy_unique_keys"]==2
    assert report["stats"]["key_collision_count"]==1
    assert report["stats"]["legacy_archive_entries"]==1
    assert report["stats"]["notion_api_calls"]==0
    assert len(report["commands"])==3
    j=[x for x in report["commands"] if x["module"]=="J"]
    assert len(j)==2
    assert all(x["quality"]=="quarantined" for x in j)
    assert all("semantic_key_collision" in x["issues"] for x in j)
    assert report["source"]["legacy_sha256"]==hashlib.sha256(db.read_bytes()).hexdigest()
    assert verify_catalog(report)


def test_repeated_build_is_byte_identical_independent_of_yaml_mtime(tmp_path):
    db,yamls=fixture(tmp_path)
    first=build_catalog(db,yamls)
    (yamls/"deploy.yaml").touch()
    second=build_catalog(db,yamls)
    assert first==second
    dest=tmp_path/"catalog.json"
    assert save_catalog(first,dest)=="created"
    assert save_catalog(second,dest)=="unchanged"
    assert load_catalog(dest)==first
    assert dest.stat().st_mode & 0o777 == 0o600
    assert set(first)=={"schema","source","stats","commands","sha256"}


def test_canonical_hash_and_publication_gate_detect_tampering(tmp_path):
    db,yamls=fixture(tmp_path)
    data=build_catalog(db,yamls)
    broken=json.loads(json.dumps(data))
    broken["commands"][0]["description"]="unsafe modified"
    with pytest.raises(CatalogError,match="digest|hash|integrity"):
        verify_catalog(broken)
    dest=tmp_path/"catalog.json"
    save_catalog(data,dest)
    # A DIFFERENT, internally well-formed catalog still must not overwrite.
    changed=json.loads(json.dumps(data))
    changed["commands"][0]["description"]="Different historical revision"
    core={key:changed[key] for key in ("schema","source","stats","commands")}
    changed["sha256"]=hashlib.sha256(json.dumps(core,sort_keys=True,
        ensure_ascii=False,separators=(",",":")).encode("utf8")).hexdigest()
    with pytest.raises(CatalogError,match="different|overwrite"):
        save_catalog(changed,dest)


def test_unknown_yaml_id_or_syntax_is_not_silently_promoted(tmp_path):
    db,yamls=fixture(tmp_path)
    (yamls/"ghost.yaml").write_text(yaml.safe_dump({
        "id":"cmd:GHOST","name":"GHOST","module_id":"module:A",
        "syntax":"CMD:GHOST","description":"Unreviewed generated instruction"
    }),encoding="utf8")
    result=build_catalog(db,yamls)
    assert len(result["commands"])==3
    assert result["stats"]["yaml_orphans"]==1
    assert result["stats"]["yaml_matches"]==1
    assert result["stats"]["auto_authorized_commands"]==0


def test_duplicate_yaml_names_or_conflicting_syntax_fail_closed(tmp_path):
    db,yamls=fixture(tmp_path)
    # Same yaml key but conflicting syntax must be visible and quarantined.
    (yamls/"second.yaml").write_text(yaml.safe_dump({
        "id":"cmd:DEPLOY","name":"DEPLOY","module_id":"module:J",
        "syntax":"CMD:DEPLOY;ADMIN:TRUE","description":"Dangerous alternative"
    }),encoding="utf8")
    result=build_catalog(db,yamls)
    assert result["stats"]["yaml_key_collisions"]==1
    assert all(x["quality"]=="quarantined" for x in result["commands"] if x["module"]=="J")


def test_unknown_command_never_falls_back_to_executable_tool(tmp_path):
    db,yamls=fixture(tmp_path)
    report=build_catalog(db,yamls)
    assert command_lookup(report,"A","@sum")["command"]=="@sum"
    assert command_lookup(report,"J","deploy") is None
    assert command_lookup(report,"A","NO_SUCH_TOOL") is None
    assert command_lookup(report,"A","@sum")["runtime_execute_allowed"] is False


def test_historical_database_must_be_opened_read_only(tmp_path):
    db,yamls=fixture(tmp_path)
    before=db.read_bytes()
    build_catalog(db,yamls)
    assert db.read_bytes()==before
    assert not (tmp_path/"old.db-wal").exists()
    assert not (tmp_path/"old.db-shm").exists()


def test_read_only_catalog_rejects_malformed_or_oversized_inputs(tmp_path):
    db,yamls=fixture(tmp_path)
    with pytest.raises(CatalogError):
        build_catalog(tmp_path/"missing.db",yamls)
    data=build_catalog(db,yamls)
    data["source"]["legacy_sha256"]="0"*64
    with pytest.raises(CatalogError):
        verify_catalog(data)


def test_catalog_cli_exports_then_creates_derived_index_without_overwriting(tmp_path):
    import subprocess
    import sys
    from experiments.vnext.catalog_index import open_search_index
    db,definitions=fixture(tmp_path)
    export=tmp_path/"first.json"
    cache=tmp_path/"first.sqlite"
    def call(*args):
        return subprocess.run(
            [sys.executable,"-m","experiments.vnext.catalog_cli",*args],
            cwd=Path(__file__).resolve().parent.parent,
            text=True,capture_output=True,timeout=15,
        )
    first=call("export","--legacy-db",str(db),"--yaml-root",str(definitions),
               "--out",str(export))
    assert first.returncode==0,first.stderr
    assert export.is_file()
    exported=load_catalog(export)
    second=call("index","--catalog",str(export),"--out",str(cache))
    assert second.returncode==0,second.stderr
    with open_search_index(cache,expected_catalog_sha256=exported["sha256"]) as con:
        assert con.execute("SELECT count(*) FROM commands").fetchone()[0]==3
    repeated=call("index","--catalog",str(export),"--out",str(cache))
    assert repeated.returncode!=0
    assert "overwrite" in repeated.stderr or "exists" in repeated.stderr
