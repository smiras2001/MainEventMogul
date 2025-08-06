# tests/test_engine.py
import pytest
from boxing.engine import MatchEngine
from boxing.models import Boxer
from dataclasses import replace

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
    red  = make_boxer("Sharp", base=12)
    red  = replace(red, accuracy=18)     # bump accuracy only

    blue = make_boxer("Blunt", base=12)

    wins = {"Sharp": 0, "Blunt": 0}
    for seed in range(200):
        outcome = MatchEngine(red, blue, seed=seed).simulate()
        if outcome["winner"]:
            wins[outcome["winner"]] += 1

    assert wins["Sharp"] > wins["Blunt"]