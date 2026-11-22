"""Release-quality triage; never auto-promote generated descriptions."""
import copy
from pathlib import Path
import pytest

from experiments.vnext.catalog import load_catalog
from experiments.vnext.quality_gate import classify_review_queue, render_review_markdown


def real_catalog():
    return load_catalog(
        Path(__file__).resolve().parents[1]
        / "experiments/vnext/catalog_snapshots/legacy-aa59150-catalog-f51e00d712c9.json"
    )


def test_queue_has_all_81_quarantined_entries_no_hidden_or_autofixed_values():
    data=real_catalog()
    q=classify_review_queue(data)
    assert q["schema"]=="comptext.codex.review.v1"
    assert q["catalog_sha256"]==data["sha256"]
    assert q["totals"]["quarantined"]==81
    assert q["totals"]["unreviewed_not_approved"]==334
    assert q["totals"]["allowed_to_execute"]==0
    assert len(q["items"])==81
    assert len(set(item["legacy_id"] for item in q["items"]))==81
    assert q["issue_counts"]=={
        "auto_generated_placeholder":78,"semantic_key_collision":2,
        "syntax_disagreement":1,"missing_syntax":1,"missing_description":1
    }
    assert all(item["review_status"]=="human_review_required" for item in q["items"])
    assert all(item["can_execute"] is False for item in q["items"])


def test_high_risk_markers_and_deploy_collision_are_distinguished():
    q=classify_review_queue(real_catalog())
    by_name={(x["module"],x["command"]):x for x in q["items"]}
    assert by_name[("A","EXEC")]["priority"]=="P0"
    assert by_name[("A","ROLLBACK")]["priority"]=="P0"
    assert by_name[("A","RISKY")]["priority"]=="P0"
    assert by_name[("J","deploy")]["priority"]=="P0"
    assert by_name[("J","DEPLOY")]["priority"]=="P0"
    assert by_name[("A","CELEBRATE")]["priority"]=="P2"
    assert by_name[("A","basic")]["priority"]=="P1"


def test_quality_gate_md_is_reproducible_explains_manual_review_and_uses_no_approvals():
    q=classify_review_queue(real_catalog())
    doc=render_review_markdown(q)
    assert doc==render_review_markdown(q)
    assert "81" in doc
    assert "P0" in doc
    assert "CMD:DEPLOY" in doc
    assert "kein" in doc.lower() or "not" in doc.lower()
    assert "approved_for_execution" not in doc
    assert doc.count("ID ")>=81


def test_tampered_catalog_is_rejected_before_queue_generation():
    data=real_catalog()
    forged=copy.deepcopy(data)
    forged["commands"][0]["quality"]="approved"
    with pytest.raises(Exception):
        classify_review_queue(forged)


def test_review_cli_emits_complete_deterministic_file_without_overwrite(tmp_path):
    import subprocess
    import sys
    root=Path(__file__).resolve().parents[1]
    source=root/"experiments/vnext/catalog_snapshots/legacy-aa59150-catalog-f51e00d712c9.json"
    out=tmp_path/"review.md"
    cmd=[sys.executable,"-m","experiments.vnext.quality_gate",
         "--catalog",str(source),"--out",str(out)]
    first=subprocess.run(cmd,cwd=root,text=True,capture_output=True,timeout=15)
    assert first.returncode==0,first.stderr
    assert out.is_file()
    assert "ID 626" in out.read_text(encoding="utf8")
    original=out.read_bytes()
    second=subprocess.run(cmd,cwd=root,text=True,capture_output=True,timeout=15)
    assert second.returncode!=0
    assert out.read_bytes()==original
