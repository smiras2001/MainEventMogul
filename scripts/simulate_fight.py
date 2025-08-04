from boxing.engine import MatchEngine
from boxing.models import Boxer

red = Boxer(
    "Red",
    jab=14,
    straight=13,
    lead_hook=12,
    hook=11,
    lead_uppercut=10,
    uppercut=9,
    block=12,
    accuracy=15,
    power=15,
    reflexes=12,
)

blue = Boxer(
    "Blue",
    jab=10,
    straight=19,
    lead_hook=14,
    hook=13,
    lead_uppercut=11,
    uppercut=13,
    block=12,
    accuracy=15,
    power=15,
    reflexes=12,
)

fight = MatchEngine(red, blue, seed=42).simulate()
print("Winner:", fight["winner"] or "Draw")
print(*fight["events"], sep="\n")
print("Scores:", fight["scores"])
