"""Contract: first 10 Codex vNext operations are planning-only, never executors."""
import copy
import json
import pytest
from pathlib import Path

from experiments.vnext.catalog import load_catalog
from experiments.vnext.core_compiler import (
    load_core_manifest,compile_plan,PlanRejected,make_agy_summary
)
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"experiments/vnext/catalog_snapshots/legacy-aa59150-catalog-f51e00d712c9.json"
CORE=ROOT/"experiments/vnext/core10.manifest.json"

def original():
    return load_catalog(CATALOG)

def plan(steps=None):
    return {"catalog_sha256":original()["sha256"],"steps":steps or [
      {"id":"step-1","command_id":1,"arguments":{"text":"Explain test outcome."}},
      {"id":"step-2","command_id":14,"arguments":{"text":"{\"a\":1}","indent":2}},
      {"id":"step-3","command_id":360,"arguments":{"target":"tests/test_parser_v5.py"}},
    ]}

def test_manifest_references_exactly_10_historical_unreviewed_and_unique_commands():
    cat=original()
    core=load_core_manifest(CORE,cat)
    assert len(core["commands"])==10
    assert len({x["command_id"] for x in core["commands"]})==10
    assert all(x["review_state"]=="draft_requires_human_review" for x in core["commands"])
    assert all(x["effect"]=="plan_only" for x in core["commands"])
    assert all(x["can_execute"] is False for x in core["commands"])
    assert not any(x["command_id"] in {32,121,146,294,293} for x in core["commands"])

def test_compiler_lossless_arguments_and_deterministic_plan_and_digest():
    cat=original()
    core=load_core_manifest(CORE,cat)
    p1=compile_plan(plan(),cat,core)
    p2=compile_plan(plan(),cat,core)
    assert p1==p2
    assert p1["schema"]=="comptext.codex.plan.v1"
    assert len(p1["steps"])==3
    assert p1["steps"][1]["arguments"]["text"]=='{"a":1}'
    assert p1["steps"][1]["arguments"]["indent"]==2
    assert p1["steps"][0]["command_id"]==1
    assert p1["steps"][2]["command_id"]==360
    assert p1["execution_allowed"] is False
    assert p1["approval_state"]=="not_requested"
    assert all(x["execution_allowed"] is False for x in p1["steps"])
    assert len(p1["plan_sha256"])==64

def test_unknown_quarantined_and_non_core_commands_fail_closed():
    cat=original()
    core=load_core_manifest(CORE,cat)
    for command_id in [32,121,146,294,293,999999,48]:
        with pytest.raises(PlanRejected):
            compile_plan(plan([{"id":"step-1","command_id":command_id,
               "arguments":{"target":"x"}}]),cat,core)

def test_no_implicit_execution_or_extra_payload_fields():
    cat=original()
    core=load_core_manifest(CORE,cat)
    for payload in [
      {"catalog_sha256":cat["sha256"],"steps":[{"id":"s-1","command_id":1,
       "arguments":{"text":"ok"},"execute":True}]},
      {"catalog_sha256":cat["sha256"],"steps":[{"id":"s-1","command_id":1,
       "arguments":{"text":"ok","tool":"shell"}}]},
      {"catalog_sha256":cat["sha256"],"steps":[{"id":"s-1","command_id":1,
       "arguments":{"text":"ok"}}],"approval_state":"approved"},
      {"catalog_sha256":"0"*64,"steps":[{"id":"s-1","command_id":1,
       "arguments":{"text":"ok"}}]},
    ]:
      with pytest.raises(PlanRejected):
          compile_plan(payload,cat,core)

def test_schema_types_limits_duplicate_ids_and_mismatched_catalog():
    cat=original();core=load_core_manifest(CORE,cat)
    for args in [
      {},{"text":""},{"text":False},{"text":"x"*17000},
    ]:
      with pytest.raises(PlanRejected):
          compile_plan(plan([{"id":"x","command_id":1,"arguments":args}]),cat,core)
    with pytest.raises(PlanRejected):
      compile_plan(plan([
        {"id":"x","command_id":1,"arguments":{"text":"one"}},
        {"id":"x","command_id":1,"arguments":{"text":"two"}}]),cat,core)
    damaged=copy.deepcopy(core)
    damaged["commands"][0]["syntax"]="modified"
    with pytest.raises(PlanRejected):
      compile_plan(plan(),cat,damaged)

def test_agy_summary_is_metadata_only_and_no_raw_text():
    cat=original();core=load_core_manifest(CORE,cat)
    payload=plan()
    payload["steps"][0]["arguments"]["text"]="secret patient data must never leak"
    compiled=compile_plan(payload,cat,core)
    summary=make_agy_summary(compiled)
    assert set(summary)=={"plan_id","plan_sha256","catalog_sha256","step_count","execution_allowed","approval_state","research_only"}
    assert summary["step_count"]==3
    assert summary["execution_allowed"] is False
    assert summary["research_only"] is True
    assert "secret patient data" not in json.dumps(summary)

def test_compiler_makes_no_mutations_to_catalog_or_manifest():
    cat=original();core=load_core_manifest(CORE,cat)
    saved=(json.dumps(cat,sort_keys=True),json.dumps(core,sort_keys=True))
    compile_plan(plan(),cat,core)
    assert saved==(json.dumps(cat,sort_keys=True),json.dumps(core,sort_keys=True))


def test_rejects_forged_plan_identity_even_if_core_digest_remains_valid():
    catalog=original()
    core=load_core_manifest(CORE,catalog)
    actual=compile_plan(plan(),catalog,core)
    altered=copy.deepcopy(actual)
    altered["plan_id"]="plan-"+"0"*24
    with pytest.raises(PlanRejected):
        make_agy_summary(altered)


def test_every_quarantined_p0_command_is_explicitly_excluded_from_core():
    from experiments.vnext.quality_gate import classify_review_queue
    catalog=original()
    core=load_core_manifest(CORE,catalog)
    q=classify_review_queue(catalog)
    p0={x["legacy_id"] for x in q["items"] if x["priority"]=="P0"}
    assert len(p0)==21
    assert not p0.intersection({x["command_id"] for x in core["commands"]})
    for id_ in sorted(p0):
        with pytest.raises(PlanRejected):
            compile_plan(plan([{"id":"step-1","command_id":id_,
                              "arguments":{"text":"must be denied"}}]),catalog,core)
