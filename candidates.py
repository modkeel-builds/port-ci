"""Mods worth porting to a Minecraft version: the most downloaded ones with no build for it.

    python tools/port_ci/candidates.py 26.3 fabric --top 200 --limit 20 > mods.json

Until the demand table (api/src/demand.ts) has enough "no build" rows, Modrinth downloads stand
in for demand: a popular mod that has not updated is in more packs that cannot move. Prints a
JSON list of {"slug", "title", "downloads", "latest"} for the port-ci workflow's matrix. Only
mods with an open source licence are listed, since a port of the rest could not be shipped.
"""
from __future__ import annotations

import argparse
import json
import sys

import requests

API = "https://api.modrinth.com/v2"
UA = {"User-Agent": "Modkeel/port-ci (github.com/Modkeel)"}
# SPDX ids whose terms let a port's jar be redistributed with its source
OPEN = {"MIT", "Apache-2.0", "LGPL-3.0-only", "LGPL-3.0-or-later", "LGPL-2.1-only",
        "LGPL-2.1-or-later", "MPL-2.0", "GPL-3.0-only", "GPL-3.0-or-later", "BSD-3-Clause",
        "BSD-2-Clause", "Unlicense", "CC0-1.0", "Zlib", "ISC"}


def num(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def releases(versions: list[str]) -> list[str]:
    return sorted((v for v in versions if all(p.isdigit() for p in v.split("."))), key=num)


def candidates(mc: str, loader: str, top: int) -> list[dict]:
    out = []
    for offset in range(0, top, 100):
        r = requests.get(f"{API}/search", headers=UA, timeout=60, params={
            "index": "downloads", "limit": min(100, top - offset), "offset": offset,
            "facets": json.dumps([["project_type:mod"], [f"categories:{loader}"],
                                  ["server_side:required", "server_side:optional"]])})
        r.raise_for_status()
        for hit in r.json()["hits"]:
            have = releases(hit["versions"])
            if mc in hit["versions"] or not have or num(have[-1]) > num(mc):
                continue
            if hit.get("license") not in OPEN:
                continue
            out.append({"slug": hit["slug"], "title": hit["title"],
                        "downloads": hit["downloads"], "latest": have[-1]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mc")
    ap.add_argument("loader")
    ap.add_argument("--top", type=int, default=200, help="most downloaded mods to look at")
    ap.add_argument("--limit", type=int, default=20, help="most to print")
    args = ap.parse_args()
    found = candidates(args.mc, args.loader, args.top)[:args.limit]
    print(f"{len(found)} mods without a {args.mc} {args.loader} build", file=sys.stderr)
    print(json.dumps(found))


if __name__ == "__main__":
    main()
