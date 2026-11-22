"""Read-only, evidence-bound Codex vNext core planning compiler.

This module never executes tools, grants approvals, resolves unsafe DSL aliases,
or interprets tasks with an LLM. It validates a fixed catalog-linked
draft vocabulary and builds a deterministic auditable *plan proposal*.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .catalog import load_catalog, verify_catalog

_CORE_SCHEMA = "comptext.codex.core10.v1"
_PLAN_SCHEMA = "comptext.codex.plan.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_STEP_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
_KIND = frozenset({"string", "boolean", "integer"})
_MAX_TEXT = 16384
_MAX_STEPS = 32


class PlanRejected(ValueError):
    """Invalid, ambiguous or unauthorized plan proposal."""


def _canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _digest(obj: object) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


def _validate_core(core: object, catalog: dict) -> dict:
    try:
        verify_catalog(catalog)
    except Exception as exc:
        raise PlanRejected("invalid catalog provenance") from exc
    if type(core) is not dict or set(core) != {"schema", "catalog_sha256", "commands", "sha256"}:
        raise PlanRejected("invalid core manifest")
    if core["schema"] != _CORE_SCHEMA or core["catalog_sha256"] != catalog["sha256"]:
        raise PlanRejected("wrong catalog or core schema")
    if type(core["sha256"]) is not str or not _DIGEST.fullmatch(core["sha256"]):
        raise PlanRejected("invalid core manifest digest")
    if core["sha256"] != _digest({k:core[k] for k in ("schema","catalog_sha256","commands")}):
        raise PlanRejected("core manifest integrity mismatch")
    cmds=core["commands"]
    if type(cmds) is not list or len(cmds)!=10:
        raise PlanRejected("core must define exactly ten draft commands")
    rows={r["legacy_id"]:r for r in catalog["commands"]}
    seen=set()
    for cmd in cmds:
        if type(cmd) is not dict or set(cmd) != {
            "command_id","module","command","syntax","description",
            "required_args","optional_args","effect","review_state",
            "can_execute","intended_use"
        }:
            raise PlanRejected("invalid core command fields")
        id_=cmd["command_id"]
        if type(id_) is not int or id_ in seen or id_ not in rows:
            raise PlanRejected("duplicate or unknown core command")
        seen.add(id_)
        src=rows[id_]
        if src["quality"] != "unreviewed" or any(
            cmd[k]!=src[k] for k in ("module","command","syntax","description")
        ) or cmd["effect"] != "plan_only" or cmd["can_execute"] is not False or (
            cmd["review_state"] != "draft_requires_human_review"
        ) or type(cmd["intended_use"]) is not str or not cmd["intended_use"].strip():
            raise PlanRejected("unreviewed core provenance or authority mismatch")
        if type(cmd["required_args"]) is not dict or not cmd["required_args"] or (
            type(cmd["optional_args"]) is not dict
        ) or len(cmd["required_args"])+len(cmd["optional_args"])>8:
            raise PlanRejected("invalid argument specification")
        if set(cmd["required_args"])&set(cmd["optional_args"]):
            raise PlanRejected("duplicated argument")
        for key,kind in [*cmd["required_args"].items(),*cmd["optional_args"].items()]:
            if type(key) is not str or not re.fullmatch(r"[a-z][a-z0-9_]{0,31}",key):
                raise PlanRejected("invalid argument name")
            if type(kind) is not str or kind not in _KIND:
                raise PlanRejected("invalid argument type")
    return core


def load_core_manifest(path: str|Path,catalog: dict) -> dict:
    p=Path(path)
    if not p.is_file() or p.is_symlink() or p.stat().st_size>131072:
        raise PlanRejected("core manifest unavailable")
    try:
        data=json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise PlanRejected("invalid core JSON") from exc
    return _validate_core(data,catalog)


def _validate_value(value:object,kind:str) -> None:
    if kind=="string" and (type(value) is not str or not value.strip()
       or len(value)>_MAX_TEXT or any(ord(ch)==0 for ch in value)):
        raise PlanRejected("invalid nonempty string argument")
    if kind=="integer" and (type(value) is not int or not 0<=value<=100):
        raise PlanRejected("invalid integer argument")
    if kind=="boolean" and type(value) is not bool:
        raise PlanRejected("invalid boolean argument")


def compile_plan(payload:dict,catalog:dict,core:dict) -> dict:
    _validate_core(core,catalog)
    if type(payload) is not dict or set(payload)!={"catalog_sha256","steps"}:
        raise PlanRejected("unexpected request fields")
    if payload["catalog_sha256"]!=catalog["sha256"]:
        raise PlanRejected("catalog digest mismatch")
    steps=payload["steps"]
    if type(steps) is not list or not 1<=len(steps)<=_MAX_STEPS:
        raise PlanRejected("invalid number of plan steps")
    definitions={item["command_id"]:item for item in core["commands"]}
    seen=set()
    result=[]
    for item in steps:
        if type(item) is not dict or set(item)!={"id","command_id","arguments"}:
            raise PlanRejected("unexpected step metadata")
        step_id=item["id"]
        if type(step_id) is not str or not _STEP_ID.fullmatch(step_id) or step_id in seen:
            raise PlanRejected("invalid or duplicate step ID")
        seen.add(step_id)
        cmd_id=item["command_id"]
        if type(cmd_id) is not int or cmd_id not in definitions:
            raise PlanRejected("quarantined/unknown/non-core command refused")
        spec=definitions[cmd_id]
        args=item["arguments"]
        if type(args) is not dict or not set(spec["required_args"]).issubset(args) or (
            set(args)-set(spec["required_args"])-set(spec["optional_args"])
        ):
            raise PlanRejected("missing or unknown arguments")
        for arg,value in args.items():
            kind=spec["required_args"].get(arg,spec["optional_args"].get(arg))
            _validate_value(value,kind)
        result.append({
            "id":step_id,
            "command_id":cmd_id,
            "semantic_key":next(row["semantic_key"] for row in catalog["commands"]
                                if row["legacy_id"]==cmd_id),
            "arguments":json.loads(_canonical(args)),
            "review_state":"draft_requires_human_review",
            "execution_allowed":False
        })
    plan_body={
        "schema":_PLAN_SCHEMA,
        "catalog_sha256":catalog["sha256"],
        "core_manifest_sha256":core["sha256"],
        "steps":result,
        "approval_state":"not_requested",
        "execution_allowed":False,
        "research_only":True,
    }
    digest=_digest(plan_body)
    return {**plan_body, "plan_sha256":digest,"plan_id":"plan-"+digest[:24]}


def make_agy_summary(compiled:dict) -> dict:
    if type(compiled) is not dict or compiled.get("schema")!=_PLAN_SCHEMA or (
        compiled.get("plan_sha256") != _digest({k:compiled[k] for k in (
          "schema","catalog_sha256","core_manifest_sha256","steps",
          "approval_state","execution_allowed","research_only"
        )})
    ) or compiled.get("plan_id")!="plan-"+compiled["plan_sha256"][:24] or (
        compiled.get("execution_allowed") is not False
    ) or compiled.get("approval_state")!="not_requested" or (
        compiled.get("research_only") is not True
    ):
        raise PlanRejected("cannot summarize unverified plan")
    return {
        "plan_id":compiled["plan_id"],"plan_sha256":compiled["plan_sha256"],
        "catalog_sha256":compiled["catalog_sha256"],"step_count":len(compiled["steps"]),
        "execution_allowed":False,"approval_state":"not_requested","research_only":True
    }
