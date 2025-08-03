#!/usr/bin/env python
from boxing.engine import MatchEngine
from boxing.models import Boxer

red = Boxer("Test Red", 14, 12, 10, 9, 8, 11)
blue = Boxer("Test Blue", 13, 11, 9, 12, 10, 8)

fight = MatchEngine(red, blue, seed=42).simulate()

print(f"Winner: {fight['winner'] or 'Draw'}")
print("\n".join(fight["events"]))
print("Scores:", fight["scores"])
