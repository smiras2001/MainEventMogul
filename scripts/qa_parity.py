#!/usr/bin/env python
import random
import statistics
from collections import Counter

from boxing.engine import MatchEngine
from boxing.models import Boxer

TEST_FIGHTS = 1000
RATINGS = dict(
    jab=10,
    straight=10,
    lead_hook=10,
    hook=10,
    lead_uppercut=10,
    uppercut=10,
    block=10,
    accuracy=10,
    power=10,
    reflexes=10,
)

red = Boxer("Red", **RATINGS)
blue = Boxer("Blue", **RATINGS)

wins = Counter()
score_diffs = []

for seed in range(TEST_FIGHTS):
    fight = MatchEngine(red, blue, seed=seed).simulate()
    score_diffs.append(fight["scores"]["Red"] - fight["scores"]["Blue"])
    if fight["winner"]:
        wins[fight["winner"]] += 1

print(f"Red wins:  {wins['Red']}")
print(f"Blue wins: {wins['Blue']}")
draws = TEST_FIGHTS - wins.total()
print(f"Draws:     {draws}")

avg_diff = statistics.mean(score_diffs)
print(f"Average score diff (Red-Blue): {avg_diff:+.2f}")
