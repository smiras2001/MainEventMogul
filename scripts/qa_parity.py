# scripts/qa_parity.py
#!/usr/bin/env python
import statistics
from collections import Counter

from boxing.engine import MatchEngine
from boxing.models import Boxer

PUNCHES = ("jab", "straight", "lead_hook", "hook", "lead_uppercut", "uppercut")
TEST_FIGHTS = 1000


def make_boxer(name: str, base: int = 10, **overrides) -> Boxer:
    """Create a 22-field Boxer with all ratings = base, then apply overrides."""
    fields = {
        # Fundamentals
        "jab": base, "straight": base, "lead_hook": base, "hook": base,
        "lead_uppercut": base, "uppercut": base, "blocking": base, "accuracy": base,
        # Boxing IQ
        "anticipation": base, "composure": base, "positioning": base, "decision": base,
        "aggression": base, "focus": base, "workrate": base, "planning": base,
        # Athleticism
        "power": base, "hand_speed": base, "foot_speed": base,
        "reflexes": base, "stamina": base, "agility": base,
    }
    fields.update(overrides)
    return Boxer(name=name, **fields)


def pacc_table(b: Boxer) -> dict[str, float]:
    """Avg(type/20, accuracy/20) for each punch (0..1)."""
    acc = b.accuracy / 20
    return {p: ((getattr(b, p) / 20) + acc) / 2 for p in PUNCHES}


def analyze(best_set: set[str], rounds: list[dict], side: str) -> tuple[float, float]:
    """Return (best_punch_share, overall_land_pct) for 'red' or 'blue'."""
    thrown = Counter()
    landed = Counter()
    for r in rounds:
        thrown.update(r[side]["thrown"])
        landed.update(r[side]["landed"])
    total_thrown = sum(thrown.values()) or 1
    total_landed = sum(landed.values())
    best_share = sum(thrown[p] for p in best_set) / total_thrown
    land_pct = (total_landed / total_thrown) if total_thrown else 0.0
    return best_share, land_pct


def run_parity():
    # Equal fighters baseline
    red = make_boxer("Red", base=10)
    blue = make_boxer("Blue", base=10)

    wins = Counter()
    score_diffs = []
    red_best_share = []
    blue_best_share = []
    red_land_pct = []
    blue_land_pct = []

    # compute best-accuracy sets once (same ratings each run)
    red_best = {p for p, v in pacc_table(red).items() if v == max(pacc_table(red).values())}
    blue_best = {p for p, v in pacc_table(blue).items() if v == max(pacc_table(blue).values())}

    for seed in range(TEST_FIGHTS):
        fight = MatchEngine(red, blue, seed=seed).simulate()
        score_diffs.append(fight["scores"]["Red"] - fight["scores"]["Blue"])
        if fight["winner"]:
            wins[fight["winner"]] += 1

        # telemetry-based punch selection & accuracy checks
        rb, rl = analyze(red_best, fight["rounds"], "red")
        bb, bl = analyze(blue_best, fight["rounds"], "blue")
        red_best_share.append(rb); red_land_pct.append(rl)
        blue_best_share.append(bb); blue_land_pct.append(bl)

    draws = TEST_FIGHTS - wins.total()
    print(f"Red wins:  {wins['Red']}")
    print(f"Blue wins: {wins['Blue']}")
    print(f"Draws:     {draws}")
    avg_diff = statistics.mean(score_diffs)
    print(f"Average score diff (Red-Blue): {avg_diff:+.2f}")

    # Telemetry summaries (should be very similar for equal fighters)
    m_red_best = statistics.mean(red_best_share)
    m_blue_best = statistics.mean(blue_best_share)
    m_red_land = statistics.mean(red_land_pct)
    m_blue_land = statistics.mean(blue_land_pct)

    print(f"Red best-punch usage:  {m_red_best:.3f}")
    print(f"Blue best-punch usage: {m_blue_best:.3f}")
    print(f"Red land% overall:     {m_red_land:.3f}")
    print(f"Blue land% overall:    {m_blue_land:.3f}")

    # ---------- Parity thresholds (tune as needed) ----------
    non_draw = wins['Red'] + wins['Blue']
    if non_draw > 0:
        red_win_rate = wins['Red'] / non_draw
        if abs(red_win_rate - 0.5) > 0.035:  # ±3.5% from 50/50
            raise SystemExit(f"FAIL: Win-rate skew {red_win_rate:.3f} > 3.5%")

    if abs(m_red_land - m_blue_land) > 0.015:  # land% within 1.5%
        raise SystemExit(f"FAIL: Land% skew {abs(m_red_land - m_blue_land):.3f} > 1.5%")

    if abs(m_red_best - m_blue_best) > 0.05:  # best-punch usage within 5%
        raise SystemExit(f"FAIL: Best-punch usage skew {abs(m_red_best - m_blue_best):.3f} > 5%")


if __name__ == "__main__":
    run_parity()
