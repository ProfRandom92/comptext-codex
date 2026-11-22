"""TDD: immutable index is a cache/projection of the validated catalog."""
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from experiments.vnext.catalog import build_catalog,save_catalog,CatalogError
from experiments.vnext.catalog_index import (
    build_search_index,open_search_index,search_catalog,lookup_catalog,
    CatalogIndexError
)
from test_vnext_catalog import fixture as source_fixture


def prepared(tmp_path):
    old,source=source_fixture(tmp_path)
    data=build_catalog(old,source)
    canonical=tmp_path/"catalog.json"
    save_catalog(data,canonical)
    out=tmp_path/"index.sqlite"
    return data,canonical,out


def test_index_build_keeps_all_entries_and_searches_only_as_metadata(tmp_path):
    data,src,out=prepared(tmp_path)
    result=build_search_index(src,out)
    assert result["rows"]==3
    assert result["catalog_sha256"]==data["sha256"]
    with open_search_index(out,expected_catalog_sha256=data["sha256"]) as con:
        assert con.execute("pragma integrity_check").fetchone()[0]=="ok"
        assert con.execute("select count(*) from commands").fetchone()[0]==3
        assert con.execute("select count(*) from command_search").fetchone()[0]==3
        assert lookup_catalog(con,module="A",command="@sum")["description"]=="Summarize provided text"
        assert lookup_catalog(con,module="J",command="deploy") is None
        rows=search_catalog(con,"summarize",limit=5)
        assert rows and rows[0]["command"]=="@sum"
        assert rows[0]["can_execute"] is False
        assert all("token" not in x for x in rows)


def test_unsafe_fts_query_is_not_executed_as_sql(tmp_path):
    data,src,out=prepared(tmp_path)
    build_search_index(src,out)
    with open_search_index(out,expected_catalog_sha256=data["sha256"]) as con:
        assert search_catalog(con,'"; DROP TABLE commands;--')==[]
        assert con.execute("select count(*) from commands").fetchone()[0]==3
        assert search_catalog(con,"zz_nonexistent")==[]


def test_index_is_immutable_and_does_not_touch_original_snapshot(tmp_path):
    data,src,out=prepared(tmp_path)
    old=src.read_bytes()
    assert build_search_index(src,out)["rows"]==3
    with pytest.raises(CatalogIndexError,match="exists|overwrite"):
        build_search_index(src,out)
    assert src.read_bytes()==old
    assert out.stat().st_mode & 0o777==0o600


def test_index_rejects_invalid_catalog_digest_and_untrusted_mutations(tmp_path):
    data,src,out=prepared(tmp_path)
    bogus=tmp_path/"bad.json"
    payload=json.loads(src.read_text())
    payload["commands"][0]["runtime_execute_allowed"]=True
    bogus.write_text(json.dumps(payload))
    with pytest.raises((CatalogError,CatalogIndexError)):
        build_search_index(bogus,out)
    assert not out.exists()


def test_index_open_fails_on_missing_or_wrong_external_digest(tmp_path):
    data,src,out=prepared(tmp_path)
    build_search_index(src,out)
    with pytest.raises(CatalogIndexError):
        with open_search_index(out,expected_catalog_sha256=None):
            pass
    with pytest.raises(CatalogIndexError):
        with open_search_index(out,expected_catalog_sha256="0"*64):
            pass
