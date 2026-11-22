"""Test AGY Rust validation as an external *structural* check, not authorization."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from experiments.vnext.catalog import load_catalog
from experiments.vnext.core_compiler import load_core_manifest, compile_plan, make_agy_summary
from test_vnext_core_compiler import plan

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"experiments/vnext/catalog_snapshots/legacy-aa59150-catalog-f51e00d712c9.json"
CORE=ROOT/"experiments/vnext/core10.manifest.json"
AGY_SCHEMA=ROOT/"experiments/vnext/agy-plan-meta.schema.json"

def agy_binary():
    path=os.environ.get("COMPTEXT_AGY7RUST_PATH")
    if not path or not Path(path).is_file():
        pytest.skip("AGY Rust binary not configured in CI")
    return path

def test_agy_schema_explicitly_only_checks_structure_not_authority():
    s=json.loads(AGY_SCHEMA.read_text(encoding="utf8"))
    assert s["schema"]=="SPARK-V7-SCHEMA"
    assert s["fixture_type"]=="synthetic_spark_style"
    assert set(s["required_field_paths"])=={
      "$.plan_id","$.plan_sha256","$.catalog_sha256","$.step_count",
      "$.execution_allowed","$.approval_state","$.research_only"
    }
    assert "not_a_signature_or_human_approval" in s["non_claims"]

def test_agy_accepts_redacted_valid_metadata_and_rejects_missing_required_field(tmp_path):
    binary=agy_binary()
    cat=load_catalog(CATALOG)
    core=load_core_manifest(CORE,cat)
    request=plan()
    request["steps"][0]["arguments"]["text"]="PERSONAL_FAKE_TEST_SECRET_NO_LEAK"
    doc=make_agy_summary(compile_plan(request,cat,core))
    target=tmp_path/"meta.json"
    target.write_text(json.dumps(doc),encoding="utf8")
    valid=subprocess.run(
      [binary,"schema-check","--input",str(target),"--schema",str(AGY_SCHEMA)],
      text=True,capture_output=True,timeout=20,
    )
    assert valid.returncode==0,valid.stdout+"\n"+valid.stderr
    assert "OK: schema-check passed" in valid.stdout
    assert "PERSONAL_FAKE_TEST_SECRET_NO_LEAK" not in valid.stdout+valid.stderr
    del doc["plan_sha256"]
    target.write_text(json.dumps(doc),encoding="utf8")
    bad=subprocess.run(
      [binary,"schema-check","--input",str(target),"--schema",str(AGY_SCHEMA)],
      text=True,capture_output=True,timeout=20,
    )
    assert bad.returncode!=0
    assert "PERSONAL_FAKE_TEST_SECRET_NO_LEAK" not in bad.stdout+bad.stderr

def test_end_to_end_compiler_cli_fails_closed_without_agy_and_writes_only_new_outputs(tmp_path):
    request=tmp_path/"request.json"
    request.write_text(json.dumps(plan()),encoding="utf8")
    output=tmp_path/"compiled.json"
    python=sys.executable
    common=[
      python,"-m","experiments.vnext.core_cli",
      "--request",str(request),"--catalog",str(CATALOG),"--core",str(CORE),
      "--output",str(output)
    ]
    no_implicit_agy=subprocess.run(common+["--agy-bin",str(tmp_path/"missing")],
       cwd=ROOT,capture_output=True,text=True,timeout=20)
    assert no_implicit_agy.returncode!=0
    assert not output.exists()
    success=subprocess.run(common,cwd=ROOT,capture_output=True,text=True,timeout=20)
    assert success.returncode==0,success.stderr
    doc=json.loads(output.read_text(encoding="utf8"))
    assert doc["execution_allowed"] is False
    assert doc["steps"][0]["command_id"]==1
    assert output.stat().st_mode&0o777==0o600
    second=subprocess.run(common,cwd=ROOT,capture_output=True,text=True,timeout=20)
    assert second.returncode!=0
    assert json.loads(output.read_text(encoding="utf8"))==doc

def test_compiler_cli_executes_actual_agy_schema_gate_before_writing_output(tmp_path):
    binary=agy_binary()
    request=tmp_path/"input.json"
    request.write_text(json.dumps(plan()),encoding="utf8")
    output=tmp_path/"output.json"
    cmd=[
      sys.executable,"-m","experiments.vnext.core_cli",
      "--request",str(request),"--catalog",str(CATALOG),"--core",str(CORE),
      "--output",str(output),"--agy-bin",binary,"--agy-schema",str(AGY_SCHEMA)
    ]
    r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=30)
    assert r.returncode==0,r.stderr
    assert json.loads(output.read_text(encoding="utf8"))["execution_allowed"] is False
    assert "AGY_GATE=PASS" in r.stdout
