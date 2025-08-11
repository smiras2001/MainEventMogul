from __future__ import annotations

import argparse
import json
from typing import Dict

from boxing.engine import MatchEngine, PUNCHES
from boxing.models import Boxer

DEFENCES = ("block", "dodge", "parry")


# ---------------------------------------------------------------------------
# Boxer helpers
# ---------------------------------------------------------------------------
def allowed_fields() -> set[str]:
    # Grab all dataclass fields from Boxer for validation
    return set(Boxer.__annotations__.keys()) - {"name"}  # name is free-form


def make_boxer(name: str, base: int, overrides: Dict[str, int]) -> Boxer:
    """Create a 22-field Boxer with all ratings = base, then apply overrides."""
    fields: Dict[str, int] = {
        # Fundamentals
        "jab": base,
        "straight": base,
        "lead_hook": base,
        "hook": base,
        "lead_uppercut": base,
        "uppercut": base,
        "blocking": base,
        "accuracy": base,
        # Boxing IQ
        "anticipation": base,
        "composure": base,
        "positioning": base,
        "decision": base,
        "aggression": base,
        "focus": base,
        "workrate": base,
        "planning": base,
        # Athleticism
        "power": base,
        "hand_speed": base,
        "foot_speed": base,
        "reflexes": base,
        "stamina": base,
        "agility": base,
    }
    fields.update(overrides)
    return Boxer(name=name, **fields)


def parse_overrides(items: list[str]) -> Dict[str, int]:
    """Parse --red/--blue overrides like accuracy=16 blocking=15."""
    out: Dict[str, int] = {}
    valid = allowed_fields()
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Bad override '{item}'. Use key=value (e.g., accuracy=16).")
        key, val = item.split("=", 1)
        key = key.strip()
        if key not in valid:
            raise SystemExit(f"Unknown field '{key}'. Allowed: {', '.join(sorted(valid))}")
        try:
            ival = int(val)
        except ValueError:
            raise SystemExit(f"Value for '{key}' must be an int (1-20), got '{val}'")
        if not (1 <= ival <= 20):
            raise SystemExit(f"Value for '{key}' must be 1-20, got {ival}")
        out[key] = ival
    return out


# ---------------------------------------------------------------------------
# Pretty printers
# ---------------------------------------------------------------------------
def pct(n: int, d: int) -> str:
    return f"{(n / d):.3f}" if d else "0.000"


def print_header(title: str):
    print("\n" + title)
    print("-" * len(title))


def print_round_table(fight: dict):
    # Round | Red T | Red L | Blue T | Blue L
    print_header("Round summary (thrown/landed)")
    print(f"{'Rnd':>3} | {'R T':>3} {'R L':>3} | {'B T':>3} {'B L':>3}")
    print("-" * 24)
    for r in fight["rounds"]:
        rt = sum(r["red"]["thrown"].values())
        rl = sum(r["red"]["landed"].values())
        bt = sum(r["blue"]["thrown"].values())
        bl = sum(r["blue"]["landed"].values())
        print(f"{r['round']:>3} | {rt:>3} {rl:>3} | {bt:>3} {bl:>3}")


def print_breakdown(fight: dict):
    # Per-punch totals across the fight
    print_header("Punch-type breakdown (totals and land%)")
    print(f"{'Punch':<13} | {'R T':>4} {'R L':>4} {'R%':>5} | {'B T':>4} {'B L':>4} {'B%':>5}")
    print("-" * 58)

    agg = {
        "red": {"thrown": {p: 0 for p in PUNCHES}, "landed": {p: 0 for p in PUNCHES}},
        "blue": {"thrown": {p: 0 for p in PUNCHES}, "landed": {p: 0 for p in PUNCHES}},
    }
    for r in fight["rounds"]:
        for side in ("red", "blue"):
            for p in PUNCHES:
                agg[side]["thrown"][p] += r[side]["thrown"][p]
                agg[side]["landed"][p] += r[side]["landed"][p]

    for p in PUNCHES:
        rt = agg["red"]["thrown"][p]
        rl = agg["red"]["landed"][p]
        bt = agg["blue"]["thrown"][p]
        bl = agg["blue"]["landed"][p]
        print(f"{p.replace('_',' '):<13} | {rt:>4} {rl:>4} {pct(rl, rt):>5} | {bt:>4} {bl:>4} {pct(bl, bt):>5}")


def print_defence(fight: dict):
    print_header("Defence usage (counts)")
    print(f"{'Mode':<8} | {'Red':>5} | {'Blue':>5}")
    print("-" * 26)
    red = {d: 0 for d in DEFENCES}
    blue = {d: 0 for d in DEFENCES}
    for r in fight["rounds"]:
        for d in DEFENCES:
            red[d] += r["red"]["defence"][d]
            blue[d] += r["blue"]["defence"][d]
    for d in DEFENCES:
        print(f"{d:<8} | {red[d]:>5} | {blue[d]:>5}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Simulate a fight and print telemetry.")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    ap.add_argument("--red-base", type=int, default=12, help="Base rating (Red)")
    ap.add_argument("--blue-base", type=int, default=12, help="Base rating (Blue)")
    ap.add_argument(
        "--red",
        action="append",
        default=[],
        metavar="key=value",
        help="Override Red rating(s), e.g., accuracy=16 blocking=15",
    )
    ap.add_argument(
        "--blue",
        action="append",
        default=[],
        metavar="key=value",
        help="Override Blue rating(s), e.g., decision=18",
    )
    ap.add_argument("--show-rounds", action="store_true", help="Show round summary table")
    ap.add_argument("--show-breakdown", action="store_true", help="Show punch-type breakdown")
    ap.add_argument("--show-defence", action="store_true", help="Show defence usage totals")
    ap.add_argument("--transcript", action="store_true", help="Print the event transcript")
    ap.add_argument("--json", metavar="PATH", help="Write full fight JSON to file")
    args = ap.parse_args()

    red_overrides = parse_overrides(args.red)
    blue_overrides = parse_overrides(args.blue)

    red = make_boxer("Red", args.red_base, red_overrides)
    blue = make_boxer("Blue", args.blue_base, blue_overrides)

    fight = MatchEngine(red, blue, seed=args.seed).simulate()

    print(f"Winner: {fight['winner'] or 'Draw'}")
    print(f"Scores: {fight['scores']}")

    if args.show_rounds:
        print_round_table(fight)
    if args.show_breakdown:
        print_breakdown(fight)
    if args.show_defence:
        print_defence(fight)
    if args.transcript:
        print_header("Transcript")
        print(*fight["events"], sep="\n")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(fight, f, indent=2)
        print(f"\nWrote JSON to {args.json}")


if __name__ == "__main__":
    main()