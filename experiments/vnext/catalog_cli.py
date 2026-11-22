"""Explicit offline, fail-closed Codex catalog rebuild CLI.

No Notion API, no Git mutations, no command execution. Outputs are new,
immutable-by-policy files. Existing paths are not overwritten.
"""
from __future__ import annotations
import argparse
import json
import sys
from .catalog import build_catalog,save_catalog,load_catalog,CatalogError
from .catalog_index import build_search_index,CatalogIndexError


def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser(prog="comptext-catalog",description=__doc__)
    subs=p.add_subparsers(dest="action",required=True)
    export=subs.add_parser("export",help="create versioned JSON from read-only source files")
    export.add_argument("--legacy-db",required=True)
    export.add_argument("--yaml-root",required=True)
    export.add_argument("--out",required=True)
    index=subs.add_parser("index",help="create disposable FTS5 SQLite index from verified JSON")
    index.add_argument("--catalog",required=True)
    index.add_argument("--out",required=True)
    inspect=subs.add_parser("inspect",help="verify digest and print content-free counts")
    inspect.add_argument("--catalog",required=True)
    args=p.parse_args(argv)
    try:
        if args.action=="export":
            report=build_catalog(args.legacy_db,args.yaml_root)
            action=save_catalog(report,args.out)
            result={"action":action,"sha256":report["sha256"],"stats":report["stats"]}
        elif args.action=="index":
            result=build_search_index(args.catalog,args.out)
            result={"action":"created","rows":result["rows"],
                    "catalog_sha256":result["catalog_sha256"]}
        else:
            report=load_catalog(args.catalog)
            result={"action":"verified","sha256":report["sha256"],"stats":report["stats"]}
    except (CatalogError,CatalogIndexError,ValueError,OSError) as error:
        print(f"catalog operation denied: {error}",file=sys.stderr)
        return 2
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
