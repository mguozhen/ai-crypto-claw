"""
Trade Journal — records decisions and triggers reflection cycles.
Inspired by LLM_trader's adaptive memory system.
"""
import json
import os
from datetime import datetime
from collections import defaultdict

JOURNAL_PATH = os.environ.get("TRADE_JOURNAL_PATH", os.path.expanduser("~/.hermes/trade_journal.json"))
RULES_PATH = os.environ.get("TRADE_RULES_PATH", os.path.expanduser("~/.hermes/trade_rules.md"))
MAX_ENTRIES = 50
REFLECTION_INTERVAL = 10


def _load_journal() -> dict:
    if os.path.exists(JOURNAL_PATH):
        with open(JOURNAL_PATH) as f:
            return json.load(f)
    return {"decisions": [], "total_count": 0}


def _save_journal(journal: dict):
    tmp = JOURNAL_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(journal, f, indent=2, default=str)
    os.replace(tmp, JOURNAL_PATH)


def log_decision(asset: str, action: str, size_pct: float, confidence: float,
                 reasoning: str, signals: list, outcome: str = "pending"):
    """Record a trading decision."""
    journal = _load_journal()
    entry = {
        "asset": asset,
        "action": action,
        "size_pct": size_pct,
        "confidence": confidence,
        "reasoning": reasoning[:500],
        "signals_summary": [{"agent": s.get("agent", ""), "stance": s.get("stance", "")}
                           for s in (signals or [])],
        "outcome": outcome,
        "timestamp": datetime.now().isoformat(),
    }
    journal["decisions"].append(entry)
    journal["decisions"] = journal["decisions"][-MAX_ENTRIES:]  # Circular buffer
    journal["total_count"] = journal.get("total_count", 0) + 1

    _save_journal(journal)

    # Trigger reflection every N decisions
    if journal["total_count"] % REFLECTION_INTERVAL == 0:
        _trigger_reflection(journal)


def update_outcome(timestamp: str, outcome: str):
    """Update a decision's outcome (win/loss/break_even)."""
    journal = _load_journal()
    for d in journal["decisions"]:
        if d["timestamp"] == timestamp:
            d["outcome"] = outcome
            break
    _save_journal(journal)


def _trigger_reflection(journal: dict):
    """Analyze patterns and generate semantic rules."""
    decisions = [d for d in journal["decisions"] if d["outcome"] in ("win", "loss")]
    if len(decisions) < 5:
        return

    # Group by (action, stance_majority)
    patterns = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
    for d in decisions:
        key = d["action"]
        patterns[key]["total"] += 1
        if d["outcome"] == "win":
            patterns[key]["wins"] += 1
        else:
            patterns[key]["losses"] += 1

    rules = []
    for action, stats in patterns.items():
        win_rate = stats["wins"] / max(stats["total"], 1)
        if stats["total"] >= 5 and win_rate >= 0.6:
            rules.append(f"✅ {action.upper()} trades perform well (win rate {win_rate:.0%}, n={stats['total']})")
        if stats["total"] >= 3 and win_rate <= 0.35:
            rules.append(f"⚠️ AVOID {action.upper()} (loss rate {1-win_rate:.0%}, n={stats['total']})")

    if rules:
        os.makedirs(os.path.dirname(RULES_PATH), exist_ok=True)
        with open(RULES_PATH, "w") as f:
            f.write("# Trade Rules (Auto-Generated)\n\n")
            f.write(f"Updated: {datetime.now().isoformat()}\n\n")
            for rule in rules:
                f.write(f"- {rule}\n")


def get_recent_decisions(asset: str = None, limit: int = 10) -> list:
    journal = _load_journal()
    decisions = journal["decisions"]
    if asset:
        decisions = [d for d in decisions if d["asset"] == asset]
    return decisions[-limit:]
