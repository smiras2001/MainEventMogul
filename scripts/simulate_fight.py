from boxing.engine import MatchEngine
from boxing.models import Boxer

# ------------------------------------------------------------------
# Helper: create a boxer with every rating set once
# ------------------------------------------------------------------
def make_boxer(
    name: str,
    *,
    base: int = 12,
    accuracy: int | None = None,
    blocking: int | None = None,
    decision: int | None = None,
) -> Boxer:
    """Return a Boxer whose ratings default to `base` and allow a few overrides."""
    vals = {k: base for k in (
        # Fundamentals
        "jab straight lead_hook hook lead_uppercut uppercut "
        "blocking accuracy".split()
        # Boxing-IQ
        + "anticipation composure positioning decision aggression focus workrate planning".split()
        # Athleticism
        + "power hand_speed foot_speed reflexes stamina agility".split()
    )}
    if accuracy  is not None: vals["accuracy"]  = accuracy
    if blocking  is not None: vals["blocking"]  = blocking
    if decision  is not None: vals["decision"]  = decision
    return Boxer(name=name, **vals)  # type: ignore[arg-type]

# ------------------------------------------------------------------
# Two demo fighters
# ------------------------------------------------------------------
red  = make_boxer("Red",  base=14, accuracy=16, decision=18)
blue = make_boxer("Blue", base=10, blocking=15, decision=6)

# ------------------------------------------------------------------
# Simulate and print
# ------------------------------------------------------------------
fight = MatchEngine(red, blue, seed=42).simulate()

print("Winner:", fight["winner"] or "Draw")
print(*fight["events"], sep="\n")
print("Scores:", fight["scores"])