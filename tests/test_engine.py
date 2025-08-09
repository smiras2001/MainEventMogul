# tests/test_engine.py
import pytest
from dataclasses import replace
from boxing.engine import MatchEngine
from boxing.models import Boxer


# ------------------------------------------------------------------
# Helper: create a boxer with every rating set to `base` (1-20)
# ------------------------------------------------------------------
def make_boxer(name: str, base: int = 10) -> Boxer:
    """Return a Boxer with all 22 ratings set to `base`."""
    return Boxer(
        # Fundamentals (8)
        jab=base, straight=base, lead_hook=base, hook=base,
        lead_uppercut=base, uppercut=base, blocking=base, accuracy=base,
        # Boxing IQ (8)
        anticipation=base, composure=base, positioning=base, decision=base,
        aggression=base, focus=base, workrate=base, planning=base,
        # Athleticism (6)
        power=base, hand_speed=base, foot_speed=base,
        reflexes=base, stamina=base, agility=base,
        name=name,
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
def test_seed_reproducible():
    """Same seed → identical fight transcript & scores."""
    red = make_boxer("Red", base=10)
    blue = make_boxer("Blue", base=10)

    fight1 = MatchEngine(red, blue, seed=123).simulate()
    fight2 = MatchEngine(red, blue, seed=123).simulate()

    assert fight1 == fight2


def test_accuracy_edge():
    """Higher accuracy should win most fights over many sims."""
    red = make_boxer("Sharp", base=12)
    red = replace(red, accuracy=18)  # bump accuracy only

    blue = make_boxer("Blunt", base=12)

    wins = {"Sharp": 0, "Blunt": 0}
    for seed in range(200):
        outcome = MatchEngine(red, blue, seed=seed).simulate()
        if outcome["winner"]:
            wins[outcome["winner"]] += 1

    assert wins["Sharp"] > wins["Blunt"]


def _decision_demo_boxer(decision: int) -> Boxer:
    """
    Boxer whose highest punch-accuracy is clearly jab/straight.
    (Other punches are lower so we don't tie for 'best'.)
    """
    return Boxer(
        # Fundamentals
        jab=15, straight=15, lead_hook=10, hook=10, lead_uppercut=10, uppercut=10,
        blocking=12, accuracy=15,
        # Boxing IQ
        anticipation=12, composure=12, positioning=12, decision=decision,
        aggression=10, focus=10, workrate=10, planning=10,
        # Athleticism
        power=12, hand_speed=12, foot_speed=12,
        reflexes=12, stamina=12, agility=12,
        name=f"Dec{decision}",
    )


def test_decision_bias():
    """
    High-Decision boxer should choose the highest PAcc punch far more often
    than a low-Decision boxer. We sample _choose_punch directly.
    """
    smart = _decision_demo_boxer(18)   # p_focus = 0.9
    dumb = _decision_demo_boxer(4)     # p_focus = 0.2

    # Use separate engines/seeds so RNG streams are independent
    eng_smart = MatchEngine(smart, dumb, seed=1)
    eng_dumb = MatchEngine(smart, dumb, seed=2)

    # Compute each boxer's punch-accuracy table once
    t_smart = eng_smart._precompute_pacc(smart)
    t_dumb = eng_dumb._precompute_pacc(dumb)

    best_smart = {p for p, v in t_smart.items() if v == max(t_smart.values())}
    best_dumb = {p for p, v in t_dumb.items() if v == max(t_dumb.values())}

    picks_smart = [eng_smart._choose_punch(smart, t_smart) for _ in range(200)]
    picks_dumb = [eng_dumb._choose_punch(dumb, t_dumb) for _ in range(200)]

    assert sum(p in best_smart for p in picks_smart) / 200 > 0.90
    assert sum(p in best_dumb for p in picks_dumb) / 200 < 0.60
