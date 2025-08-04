from boxing.engine import MatchEngine
from boxing.models import Boxer

red = Boxer(
    "Red", 14, 13, 12, 11, 10, 9,
    block=12, accuracy=14,
    power=15, reflexes=11
)

blue = Boxer(
    "Blue", 13, 14, 10, 12, 9, 11,
    block=11, accuracy=13,
    power=14, reflexes=12
)

fight = MatchEngine(red, blue, seed=42).simulate()
print("Winner:", fight["winner"] or "Draw")
print(*fight["events"], sep="\n")
print("Scores:", fight["scores"])