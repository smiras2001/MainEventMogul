from __future__ import annotations

import random
from typing import List

from . import prob
from boxing.prob import block_score, dodge_score, parry_score
from .models import Boxer

ROUNDS = 12
PUNCHES = ("jab", "straight", "lead_hook", "hook", "lead_uppercut", "uppercut")


class MatchEngine:
    """Runs a 12-round fight with simple land/evade logic."""

    def __init__(self, red: Boxer, blue: Boxer, *, seed: int | None = None):
        self.red, self.blue = red, blue
        self.rng = random.Random(seed)
        self.events: List[str] = []
        self.scores = {red.name: 0, blue.name: 0}  # 10-10 per round placeholder

    # public API
    def simulate(self) -> dict:
        for rnd in range(1, ROUNDS + 1):
            self._simulate_round(rnd)
        winner = self._winner()
        return {"winner": winner, "scores": self.scores, "events": self.events}

    # helpers -----------------------------------------------------------
    def _simulate_round(self, rnd: int) -> None:
        red_landed = blue_landed = 0

        # each fighter throws two punches (example logic)
        for punch in self.rng.sample(PUNCHES, k=2):
            if self._throw(self.red, self.blue, punch, rnd):
                red_landed += 1
            if self._throw(self.blue, self.red, punch, rnd):
                blue_landed += 1
        # -------- 10-Point Must placeholder ---------
        if red_landed > blue_landed:
            self.scores[self.red.name] += 10
            self.scores[self.blue.name] += 9
        elif blue_landed > red_landed:
            self.scores[self.blue.name] += 10
            self.scores[self.red.name] += 9
        else:  # tie on landed punches
            self.scores[self.red.name] += 10
            self.scores[self.blue.name] += 10


    def _throw(self, attacker: Boxer, defender: Boxer, punch: str, rnd: int) -> bool:
        # 1) punch accuracy (0-1)
        punch_acc = (
            (getattr(attacker, punch) / 20) + (attacker.accuracy / 20)
        ) / 2

        # 2) defender’s three defence scores
        block  = block_score(defender)
        dodge  = dodge_score(defender)
        parry  = parry_score(defender)

        # 3) Decision rule
        p_focus = defender.decision / 20
        if self.rng.random() < p_focus:
            chosen = max(block, dodge, parry)
        else:
            total = block + dodge + parry
            roll  = self.rng.random()
            cutoff_block = block / total
            cutoff_dodge = cutoff_block + dodge / total
            if roll < cutoff_block:
                chosen = block
            elif roll < cutoff_dodge:
                chosen = dodge
            else:
                chosen = parry

        # 4) land probability
        p_land = punch_acc / (punch_acc + chosen)
        landed = self.rng.random() < p_land

        # 5) narrative
        if landed:
            verb = "lands"
            subj = attacker.name
        else:
            # choose wording based on which defence actually stopped the punch
            if chosen == block:
                verb = "blocked"
            else:  # chosen was dodge or parry
                verb = "misses"
            subj = attacker.name  # attacker is the one whose punch failed

        self.events.append(
            f"Round {rnd}: {subj} {verb} a {punch.replace('_', ' ')}."
        )

        return landed

    def _winner(self) -> str | None:
        r, b = self.red.name, self.blue.name
        return (
            r
            if self.scores[r] > self.scores[b]
            else b if self.scores[b] > self.scores[r] else None
        )
