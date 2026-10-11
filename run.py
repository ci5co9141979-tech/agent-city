#!/usr/bin/env python3
"""Start the city:  python3 run.py [micro_app template_vault printables luts course]

Runs every product line through research -> build -> QA -> copy -> package,
with agents coordinating through the shared board. No input needed."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from city import llm  # noqa: E402
from city.agents import Builder, Copywriter, Designer, Mayor, Publisher, QA, Researcher  # noqa: E402
from city.board import Board  # noqa: E402
from city.catalog import CATALOG  # noqa: E402
from city.dashboard import render  # noqa: E402


def main(keys, board=None):
    if board is None:
        db = ROOT / "out" / "city.db"
        db.parent.mkdir(exist_ok=True)
        if db.exists():
            db.unlink()
        board = Board(db)
    mayor = Mayor(board)
    citizens = [Researcher(board), Builder(board), QA(board), Designer(board), Copywriter(board), Publisher(board)]
    mayor.plan(keys)

    for _ in range(200):  # safety cap
        worked = any([a.step() for a in citizens])
        mayor.supervise()
        if not worked and board.pending() == 0:
            break
        if not worked:
            break

    done = [k for k in keys if any(t["category"] == k and t["role"] == "publisher" and t["status"] == "done" for t in board.tasks())]
    mayor.say("all", "city", f"Run complete: {len(done)}/{len(keys)} product lines shipped to launch kit: {', '.join(done)}")
    render(board, ROOT / "out" / "dashboard.html", llm.available())
    print(f"\nDashboard: {ROOT / 'out' / 'dashboard.html'}")
    return 0 if len(done) == len(keys) else 1


def weekly():
    """One new product per week, fully unattended. Prints a report and writes out/weekly_report.md."""
    from city.muse import Muse
    db = ROOT / "out" / "city.db"
    db.parent.mkdir(exist_ok=True)
    if db.exists():
        db.unlink()
    board = Board(db)
    muse = Muse(board)
    key, entry = muse.pick()
    if not key:
        print("Nothing to build:", entry)
        (ROOT / "out" / "weekly_report.md").write_text(f"# Weekly run\n\nNothing built: {entry}\n")
        return 0
    CATALOG[key] = entry
    code = main([key], board)
    (ROOT / "out" / "weekly_report.md").write_text(
        f"# Weekly product: {entry['name']}\n\n- Category: {entry['category']}\n- Price: ${entry['price']}\n"
        f"- Status: {'shipped to launch kit' if code == 0 else 'FAILED (see out/dashboard.html)'}\n"
        f"- Bundle: out/{key}/{key}_bundle.zip\n- Listing: out/{key}/listing.md\n- Images: out/{key}/images/\n")
    return code


if __name__ == "__main__":
    if "--weekly" in sys.argv:
        sys.exit(weekly())
    sys.exit(main(sys.argv[1:] or list(CATALOG)))
