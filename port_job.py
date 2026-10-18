"""One port-ci job: get a mod for a Minecraft version the way `modkeel get` does, boot a server
with it, and write what happened to result.json.

    python port_job.py emi 26.3 fabric --out out

Runs the same strategies as the CLI (official, older official, forks and community ports,
relaxed range), so a result here is what a player running `modkeel get` would get. Only
the published modkeel package is used, never lab code: this file runs in a public repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from modkeel.commands._shared import resolve_github_token
from modkeel.config import ModkeelConfig
from modkeel.constants import MODKEEL_VERSION
from modkeel.core.engine import GetRequest, get_mod
from modkeel.core.events import SourceTried
from modkeel.core.text import print_event


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mod")
    ap.add_argument("mc")
    ap.add_argument("loader")
    ap.add_argument("--loader-version")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    trail: list[dict] = []

    def events(event) -> None:
        print_event(event)
        if isinstance(event, SourceTried):
            trail.append({"strategy": event.strategy, "ok": event.ok, "detail": event.detail})

    start = time.monotonic()
    request = GetRequest(args.mod, args.mc, args.loader, args.loader_version, args.out,
                         verify_runtime=True, github_token=resolve_github_token(
                             os.environ.get("GITHUB_TOKEN"), ModkeelConfig()))
    result = get_mod(request, events=events)
    got = result.delivered
    row = {"mod": args.mod, "mc": args.mc, "loader": args.loader, "modkeel": MODKEEL_VERSION,
           "seconds": round(time.monotonic() - start), "ok": got is not None, "trail": trail}
    if got is not None:
        jar = Path(got.jar_path)
        row.update(jar=jar.name, sha1=hashlib.sha1(jar.read_bytes()).hexdigest(),
                   version=got.mod_version, verb=got.verb, evidence=list(got.evidence),
                   source=next((s["strategy"] for s in trail if s["ok"]), None),
                   caveat=getattr(got, "caveat", None))
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (Path(args.out) / "result.json").write_text(json.dumps(row, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in row.items() if k != "trail"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
