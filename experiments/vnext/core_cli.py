"""Offline Codex planning CLI with optional AGY Rust structural gate.

Only proposals; never runs generated steps, grants authorization or modifies
the original catalog. AGY sees a redacted, fixed-field header only.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .catalog import load_catalog
from .core_compiler import (
    PlanRejected, load_core_manifest, compile_plan, make_agy_summary
)


def _run_agy(binary: str, schema: str, plan: dict) -> bool:
    bp=Path(binary)
    sp=Path(schema)
    if not bp.is_file() or not os.access(bp,os.X_OK) or not sp.is_file():
        raise PlanRejected("AGY binary or schema unavailable")
    if sp.resolve()!=Path(__file__).with_name("agy-plan-meta.schema.json").resolve():
        raise PlanRejected("AGY schema must be the pinned research contract")
    # No argument text, real user content, code or source references leave
    # the private compiler process. AGY reads only fixed scalar metadata.
    public=make_agy_summary(plan)
    with tempfile.TemporaryDirectory(prefix="comptext-agy-gate-") as folder:
        path=Path(folder)/"summary.json"
        path.write_text(json.dumps(public,sort_keys=True),encoding="utf8")
        os.chmod(path,0o600)
        try:
            p=subprocess.run([str(bp),"schema-check","--input",str(path),
                 "--schema",str(sp)],capture_output=True,text=True,
                 timeout=20,check=False)
        except (OSError,subprocess.TimeoutExpired) as exc:
            raise PlanRejected("AGY schema gate unavailable") from exc
        if p.returncode!=0 or "OK: schema-check passed" not in p.stdout:
            raise PlanRejected("AGY schema gate rejected proposal")
    return True


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request",required=True)
    parser.add_argument("--catalog",required=True)
    parser.add_argument("--core",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--agy-bin")
    parser.add_argument("--agy-schema")
    args=parser.parse_args(argv)
    try:
        p=Path(args.request)
        if not p.is_file() or p.stat().st_size>524288:
            raise PlanRejected("invalid input request")
        request=json.loads(p.read_text(encoding="utf8"))
        cat=load_catalog(args.catalog)
        core=load_core_manifest(args.core,cat)
        planned=compile_plan(request,cat,core)
        agy_ran=False
        if args.agy_schema and not args.agy_bin:
            raise PlanRejected("AGY binary required when schema gate requested")
        if args.agy_bin:
            agy_ran=_run_agy(args.agy_bin,args.agy_schema or str(
                 Path(__file__).with_name("agy-plan-meta.schema.json")),planned)
        dest=Path(args.output)
        if dest.exists() or dest.is_symlink():
            raise PlanRejected("output already exists; refusing overwrite")
        body=json.dumps(planned,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
        if len(body.encode("utf8"))>524288:
            raise PlanRejected("plan too large")
        dest.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,"w",encoding="utf8") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
    except (PlanRejected,ValueError,OSError,TypeError) as error:
        print("PLAN_DENIED: "+str(error),file=sys.stderr)
        return 2
    print("COMPTEXT_PLAN=CREATED; EXECUTION_ALLOWED=FALSE; AGY_GATE="+(
        "PASS" if agy_ran else "NOT_RUN"
    ))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
