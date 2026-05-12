#!/usr/bin/env python3
"""bbl_review — chronological re-review queue for enriched cards.

The premise: the bbl-researcher prompt evolves. Cards enriched under v1 of
the prompt may have confabulations the v2 / v3 prompt would catch. Rather
than stamp a `prompt_version: N` field into every card's frontmatter (noisy,
needs maintenance), we just track a SIMPLE ORDERED LIST of card paths in
chronological enrichment order. Position in the list ≈ prompt-version era.

A cursor tracks "everything before this index has been re-reviewed under the
current prompt." When you tighten the prompt and want to upgrade older cards,
you walk the queue from the top, re-running vision on each card. Cursor
advances. Eventually all cards are at the latest prompt.

When the prompt changes substantially again, you can rewind the cursor to 0
and walk through again. The list is the version control.

Files:
  reports/review_queue.txt   — one card-MD path per line, oldest enrichment first
  reports/review_cursor.txt  — single integer (0-indexed) of next card to review

Usage:
  python bbl_review.py build              # one-time: scan git history, produce queue
  python bbl_review.py status             # show cursor / total / remaining
  python bbl_review.py next [N=13]        # print next N card paths (for fan-out)
  python bbl_review.py advance [N=1]      # advance cursor by N (after reprocessing)
  python bbl_review.py rewind [N|all]     # rewind cursor by N (or to start) for prompt-change re-walk
  python bbl_review.py append <path>      # append a card path to the queue (after fresh enrichment)

Workflow:
  1. python bbl_review.py build           # one time
  2. python bbl_review.py status          # check progress
  3. python bbl_review.py next 13         # see what's up next
  4. <fan out 13 bbl-researcher subagents on those paths>
  5. python bbl_review.py advance 13      # cursor advances
  6. repeat 3–5 until status shows 0 remaining
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
QUEUE_FILE = ROOT / "reports" / "review_queue.txt"
CURSOR_FILE = ROOT / "reports" / "review_cursor.txt"

# Match commit subjects whose work was an enrichment pass. Loose pattern —
# better to over-include and dedup than miss a commit.
ENRICH_SUBJECT_RE = re.compile(
    r"\b(enrich|vision|fan out|first 19)\b", re.IGNORECASE
)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def is_currently_enriched(card_path: Path) -> bool:
    """Returns True if the card MD currently has a non-empty tags_hub."""
    try:
        text = card_path.read_text(encoding="utf-8")
    except OSError:
        return False
    m = FRONTMATTER_RE.match(text)
    if not m:
        return False
    fm = m.group(1)
    hub_match = re.search(r"^tags_hub:\s*(.+)$", fm, re.M)
    if not hub_match:
        return False
    val = hub_match.group(1).strip()
    return bool(val) and val not in ("[]", '""', "''")


def build_queue() -> list[str]:
    """Walk git log oldest-first, dedup card paths from enrichment commits."""
    cmd = ["git", "log", "--reverse", "--format=%H|%s", "--", "cards/"]
    log = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

    queue: list[str] = []
    seen: set[str] = set()
    for line in log.strip().split("\n"):
        if "|" not in line:
            continue
        sha, _, subject = line.partition("|")
        if not ENRICH_SUBJECT_RE.search(subject):
            continue
        files_cmd = ["git", "show", "--name-only", "--format=", sha]
        files = subprocess.run(files_cmd, capture_output=True, text=True, check=True).stdout
        for f in files.strip().split("\n"):
            f = f.strip()
            if not f or not f.endswith(".md"):
                continue
            if not f.startswith("cards/"):
                continue
            if f in seen:
                continue
            # Filter to currently-enriched cards only — files that have been
            # csv2mdbot-touched but never vision-pass'd shouldn't be in the
            # review queue.
            if not is_currently_enriched(ROOT / f):
                continue
            queue.append(f)
            seen.add(f)
    return queue


def read_cursor() -> int:
    if not CURSOR_FILE.exists():
        return 0
    try:
        return int(CURSOR_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return 0


def write_cursor(n: int) -> None:
    CURSOR_FILE.write_text(str(n) + "\n", encoding="utf-8")


def read_queue() -> list[str]:
    if not QUEUE_FILE.exists():
        return []
    return [
        line.strip()
        for line in QUEUE_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_queue(items: list[str]) -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text("\n".join(items) + "\n", encoding="utf-8")


def cmd_build(_args: argparse.Namespace) -> int:
    queue = build_queue()
    write_queue(queue)
    if not CURSOR_FILE.exists():
        write_cursor(0)
    print(f"Built review queue: {len(queue)} cards")
    print(f"  Queue: {QUEUE_FILE}")
    print(f"  Cursor: {CURSOR_FILE} (current: {read_cursor()})")
    return 0


def _count_enriched_on_disk() -> int:
    """Count cards in cards/ whose frontmatter currently shows a non-empty
    tags_hub. Used to detect drift between the queue file and reality."""
    cards_dir = ROOT / "cards"
    if not cards_dir.exists():
        return 0
    count = 0
    for p in cards_dir.rglob("*.md"):
        if any(seg.startswith("_") for seg in p.parts):
            continue  # skip _hubs/_symbols/_artists/_images
        if is_currently_enriched(p):
            count += 1
    return count


def cmd_status(_args: argparse.Namespace) -> int:
    queue = read_queue()
    cursor = read_cursor()
    total = len(queue)
    remaining = max(0, total - cursor)
    pct = (cursor / total * 100) if total else 0.0
    on_disk = _count_enriched_on_disk()
    drift = on_disk - total
    print(f"Total enriched cards in queue:  {total}")
    print(f"Enriched cards on disk:         {on_disk}")
    print(f"Cursor (next to review):        {cursor}")
    print(f"Reviewed so far:                {cursor}  ({pct:.1f}%)")
    print(f"Remaining:                      {remaining}")
    if drift > 0:
        print(f"\n  ! Queue is stale by {drift} card(s) — enriched on disk but not in queue.")
        print(f"    Run `python bbl_review.py build` to refresh the queue.")
    elif drift < 0:
        print(f"\n  ! Queue lists {-drift} card(s) that are no longer enriched on disk.")
        print(f"    (Possible: cards reverted or moved.) Run `python bbl_review.py build`.")
    if cursor < total:
        print(f"\nNext card: {queue[cursor]}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    queue = read_queue()
    cursor = read_cursor()
    n = args.n
    chunk = queue[cursor : cursor + n]
    if not chunk:
        print("(queue exhausted)")
        return 0
    for p in chunk:
        # Resolve to absolute path for easy paste into agent dispatch
        print((ROOT / p).resolve())
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    queue = read_queue()
    cursor = read_cursor()
    new_cursor = min(len(queue), cursor + args.n)
    write_cursor(new_cursor)
    print(f"Cursor: {cursor} -> {new_cursor}  ({new_cursor}/{len(queue)})")
    return 0


def cmd_rewind(args: argparse.Namespace) -> int:
    queue = read_queue()
    cursor = read_cursor()
    if args.n == "all":
        new_cursor = 0
    else:
        try:
            n = int(args.n)
        except ValueError:
            print(f"ERROR: rewind expects an integer or 'all', got {args.n!r}", file=sys.stderr)
            return 1
        new_cursor = max(0, cursor - n)
    write_cursor(new_cursor)
    print(f"Cursor: {cursor} -> {new_cursor}  ({new_cursor}/{len(queue)})")
    return 0


def cmd_append(args: argparse.Namespace) -> int:
    queue = read_queue()
    p = args.path
    # Normalize to project-relative cards/...
    abs_path = Path(p).resolve()
    try:
        rel = abs_path.relative_to(ROOT.resolve())
    except ValueError:
        print(f"ERROR: path is not inside the project: {p}", file=sys.stderr)
        return 1
    rel_str = str(rel).replace("\\", "/")
    if rel_str in queue:
        print(f"already in queue: {rel_str}")
        return 0
    queue.append(rel_str)
    write_queue(queue)
    print(f"appended: {rel_str}")
    print(f"queue size: {len(queue)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("build", help="Scan git history and rebuild the review queue.")
    sp.set_defaults(func=cmd_build)

    sp = sub.add_parser("status", help="Show cursor, total, remaining.")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("next", help="Print the next N card paths from the queue.")
    sp.add_argument("n", type=int, nargs="?", default=13)
    sp.set_defaults(func=cmd_next)

    sp = sub.add_parser("advance", help="Advance the cursor by N.")
    sp.add_argument("n", type=int, nargs="?", default=1)
    sp.set_defaults(func=cmd_advance)

    sp = sub.add_parser("rewind", help="Rewind the cursor by N (or 'all' to reset to 0).")
    sp.add_argument("n", default="1")
    sp.set_defaults(func=cmd_rewind)

    sp = sub.add_parser("append", help="Append a card path to the end of the queue.")
    sp.add_argument("path")
    sp.set_defaults(func=cmd_append)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
