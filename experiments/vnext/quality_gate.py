"""Read-only quality review triage for the recovered CompText Codex.

Creates a deterministic *manual* review queue; it never invents command
semantics, corrects placeholders, signs evidence or approves an executable tool.
"""
from __future__ import annotations

from collections import Counter
import re

from .catalog import verify_catalog

PRIORITY_0 = re.compile(
    r"(?:^|[_:.@-])(?:"
    r"EXEC|DEPLOY|ROLLBACK|RISKY|SEC_ALLOW|SEC_POLICY|SEC_RBAC|"
    r"SEC_AUDIT|MCP_TOOL|MCPS|MCPC|EXPORT|LOAD|SAVE|FETCH|"
    r"CONFIG_SET|TOOL|CALL|CLEANUP|RESET"
    r")(?:$|[_:.@-])", re.IGNORECASE
)
PRIORITY_1 = re.compile(
    r"(?:^|[_:.@-])(?:BUILD|AUTH|LOG|QUEUE|PROC|CONF|CFG|CACHE|STATE|PRIO|DATA|WASM)(?:$|[_:.@-])",
    re.IGNORECASE
)


def _priority(row: dict) -> str:
    if "semantic_key_collision" in row["issues"] or PRIORITY_0.search(row["command"]):
        return "P0"
    if (
        "missing_syntax" in row["issues"]
        or "missing_description" in row["issues"]
        or PRIORITY_1.search(row["command"])
    ):
        return "P1"
    return "P2"


def classify_review_queue(snapshot: dict) -> dict:
    """Produce all quarantined records, with exact issue provenance."""
    verify_catalog(snapshot)
    quarantined = [
        row for row in snapshot["commands"] if row["quality"] == "quarantined"
    ]
    issues = Counter(issue for row in quarantined for issue in row["issues"])
    items = []
    for row in quarantined:
        if row["runtime_execute_allowed"] is not False:
            raise ValueError("unreviewed command may not execute")
        items.append({
            "legacy_id": row["legacy_id"],
            "module": row["module"],
            "command": row["command"],
            "semantic_key": row["semantic_key"],
            "syntax": row["syntax"],
            "description": row["description"],
            "issues": sorted(row["issues"]),
            "priority": _priority(row),
            "source_yaml": [
                {"file": provenance["file"], "sha256":provenance["sha256"]}
                for provenance in row["yaml_provenance"]
            ],
            "review_status": "human_review_required",
            "required_checks": [
                "Confirm exact semantics and command parameter schema",
                "Compare original examples and negative cases with the source",
                "Review effect class and required scopes independently",
                "Preserve provenance and version the corrected command",
                "Re-run tests; do not infer authorization from a corrected description",
            ],
            "can_execute": False,
        })
    order = {"P0": 0, "P1": 1, "P2": 2}
    items.sort(key=lambda row: (order[row["priority"]],row["module"],row["command"].casefold(),row["legacy_id"]))
    return {
        "schema": "comptext.codex.review.v1",
        "catalog_sha256": snapshot["sha256"],
        "totals": {
            "commands": len(snapshot["commands"]),
            "quarantined": len(quarantined),
            "unreviewed_not_approved": snapshot["stats"]["unreviewed_rows"],
            "allowed_to_execute": 0,
            "priority_P0": sum(x["priority"] == "P0" for x in items),
            "priority_P1": sum(x["priority"] == "P1" for x in items),
            "priority_P2": sum(x["priority"] == "P2" for x in items),
        },
        "issue_counts": dict(sorted(issues.items())),
        "items": items,
    }


def render_review_markdown(queue: dict) -> str:
    """Human-readable deterministic review packet, explicitly no approval."""
    totals = queue["totals"]
    lines = [
        "# CompText Codex — manuelle Qualitätsprüfung (VNext)",
        "",
        "Quelle: versionierter Git-Katalog, SHA-256 `"+queue["catalog_sha256"]+"`.",
        "",
        "**Wichtig:** Dies ist eine Prüfwarteschlange. **Kein** Eintrag ist zur Ausführung freigegeben.",
        "",
        f"**Datensätze:** {totals['commands']} gesamt, {totals['quarantined']} gesperrt, "
        f"{totals['unreviewed_not_approved']} noch ungeprüft.",
        "",
        "Prioritäten sind **Review-Prioritäten**, keine automatischen Gefahrenbewertungen.",
        f"P0: {totals['priority_P0']}, P1: {totals['priority_P1']}, P2: {totals['priority_P2']}.",
        "",
        "## Ursachen",
        "",
    ]
    lines += [f"- `{issue}`: {count}" for issue,count in queue["issue_counts"].items()]
    lines += ["", "## Vollständige Prüfwarteschlange", ""]
    for item in queue["items"]:
        syntax = item["syntax"].replace("`", "'").replace("\n", " ")[:300]
        description = item["description"].replace("`", "'").replace("\n", " ")[:500]
        sources = ", ".join(x["file"] for x in item["source_yaml"]) or "keine YAML-Einzeldatei"
        lines += [
            f"### {item['priority']} — ID {item['legacy_id']}: `{item['module']}:{item['command']}`",
            "",
            f"- Syntax: `{syntax}`",
            f"- Vorhandene Beschreibung: {description or 'fehlt'}",
            f"- Ursachen: {', '.join(item['issues'])}",
            f"- Herkunft: {sources}",
            "- Maßnahmen: Semantik, Parameter, negative Tests, Seiteneffekte und erforderliche Scopes "
            "**fachlich prüfen**; bis dahin keine Ausführung.",
            "",
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Write an immutable human review packet from a previously checked catalog."""
    import argparse
    import os
    from pathlib import Path
    from .catalog import CatalogError, load_catalog

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        queue = classify_review_queue(load_catalog(args.catalog))
        result = render_review_markdown(queue)
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf8") as writer:
            writer.write(result)
            writer.flush()
            os.fsync(writer.fileno())
        print("Manual review queue created:", output, "rows:", len(queue["items"]))
        return 0
    except (CatalogError, OSError, ValueError) as exc:
        print("manual review export denied:", str(exc), file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
