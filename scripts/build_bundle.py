#!/usr/bin/env python3
import argparse, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml  # PyYAML
except Exception as e:
    print("PyYAML is required. Install: pip install pyyaml", file=sys.stderr)
    raise

try:
    import jsonschema
except Exception:
    print("jsonschema is required. Install: pip install jsonschema", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"

def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def validate(instance: Any, schema_path: Path) -> None:
    schema = load_json(schema_path)
    jsonschema.validate(instance=instance, schema=schema)

def read_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a YAML mapping/object.")
    return data

def stable_and_exposed(obj: Dict[str, Any], allow_experimental: bool) -> bool:
    if not obj.get("mcp_exposed", False):
        return False
    if allow_experimental:
        return obj.get("stability") in {"experimental","stable","frozen"}
    return obj.get("stability") in {"stable","frozen"}

def normalize_whitespace(s: str) -> str:
    s = re.sub(r"\r\n?", "\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s

def build_bundle(codex_dir: Path, version: str, repo: str, git_commit: str, allow_experimental: bool) -> Dict[str, Any]:
    module_schema = SCHEMAS / "module.schema.json"
    command_schema = SCHEMAS / "command.schema.json"
    profile_schema = SCHEMAS / "profile.schema.json"
    bundle_schema = SCHEMAS / "bundle.schema.json"

    modules: List[Dict[str, Any]] = []
    commands: List[Dict[str, Any]] = []
    profiles: List[Dict[str, Any]] = []

    for p in sorted((codex_dir / "modules").glob("*.yaml")):
        m = read_yaml(p)
        if "text_compact" in m:
            m["text_compact"] = normalize_whitespace(m["text_compact"])
        validate(m, module_schema)
        if stable_and_exposed(m, allow_experimental):
            modules.append(m)

    for p in sorted((codex_dir / "commands").glob("*.yaml")):
        c = read_yaml(p)
        if "text_compact" in c:
            c["text_compact"] = normalize_whitespace(c["text_compact"])
        validate(c, command_schema)
        if stable_and_exposed(c, allow_experimental):
            commands.append(c)

    for p in sorted((codex_dir / "profiles").glob("*.yaml")):
        pr = read_yaml(p)
        if "text_compact" in pr:
            pr["text_compact"] = normalize_whitespace(pr["text_compact"])
        validate(pr, profile_schema)
        if stable_and_exposed(pr, allow_experimental):
            profiles.append(pr)

    by_module_code = {m["code"]: m["id"] for m in modules}
    by_command_name = {c["name"]: c["id"] for c in commands}

    by_alias: Dict[str, str] = {}
    for c in commands:
        for a in c.get("aliases", []):
            by_alias[a] = c["id"]

    search = []
    for m in modules:
        search.append({
            "id": m["id"],
            "kind": "module",
            "module_code": m["code"],
            "stability": m["stability"],
            "mcp_exposed": m["mcp_exposed"],
            "keywords": list(set((m.get("tags") or []) + [m["code"], m["name"]])),
            "text_compact": m["text_compact"]
        })
    for c in commands:
        # module_code from module_id via by_module_code reverse
        module_code = None
        for mm in modules:
            if mm["id"] == c["module_id"]:
                module_code = mm["code"]; break
        module_code = module_code or "?"
        kws = list(set((c.get("keywords") or []) + [c["name"]] + (c.get("aliases") or []) + [module_code]))
        search.append({
            "id": c["id"],
            "kind": "command",
            "module_code": module_code,
            "stability": c["stability"],
            "mcp_exposed": c["mcp_exposed"],
            "keywords": kws,
            "text_compact": c["text_compact"]
        })
    for pr in profiles:
        search.append({
            "id": pr["id"],
            "kind": "profile",
            "module_code": "-",
            "stability": pr["stability"],
            "mcp_exposed": pr["mcp_exposed"],
            "keywords": list(set((pr.get("keywords") or []) + [pr["name"], pr["type"]])),
            "text_compact": pr["text_compact"]
        })

    bundle = {
        "meta": {
            "codex_name": "CompText",
            "version": version,
            "build_time_utc": datetime.now(timezone.utc).isoformat(),
            "git_commit": git_commit,
            "schema_version": "1.0",
            "source": {"repo": repo, "path": str(codex_dir)}
        },
        "modules": modules,
        "commands": commands,
        "profiles": profiles,
        "indexes": {
            "by_module_code": by_module_code,
            "by_command_name": by_command_name,
            "by_alias": by_alias,
            "search": search
        }
    }

    validate(bundle, bundle_schema)
    return bundle

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codex-dir", default="codex", help="Path to codex directory (contains modules/commands/profiles)")
    ap.add_argument("--out", default="dist/codex.bundle.json", help="Output bundle path")
    ap.add_argument("--version", required=True, help="Codex version (e.g., 3.5.1)")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY",""), help="Repo slug org/name")
    ap.add_argument("--git-commit", default=os.environ.get("GITHUB_SHA","")[:12], help="Git commit hash")
    ap.add_argument("--allow-experimental", action="store_true", help="Include experimental items if mcp_exposed=true")
    args = ap.parse_args()

    codex_dir = (ROOT / args.codex_dir).resolve()
    out_path = (ROOT / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not codex_dir.exists():
        raise SystemExit(f"codex dir not found: {codex_dir}")

    bundle = build_bundle(codex_dir, args.version, args.repo or "", args.git_commit or "", args.allow_experimental)
    out_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote bundle: {out_path} (modules={len(bundle['modules'])}, commands={len(bundle['commands'])}, profiles={len(bundle['profiles'])})")

if __name__ == "__main__":
    main()
