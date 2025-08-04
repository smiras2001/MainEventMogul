from __future__ import annotations
import random
from typing import List

from .models import Boxer
from . import prob

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
        for punch in self.rng.sample(PUNCHES, k=2):  # each fighter throws one random punch
            self._throw(self.red, self.blue, punch, rnd)
            self._throw(self.blue, self.red, punch, rnd)
        # temporary even scoring
        self.scores[self.red.name] += 10
        self.scores[self.blue.name] += 10

    def _throw(self, attacker: Boxer, defender: Boxer, punch: str, rnd: int):
        landed = prob.hit(
            attacker.accuracy,
            defender.block,
            defender.reflexes,
            self.rng,  # ← use local RNG
        )
        verb = "lands" if landed else "is blocked"
        subj = attacker.name if landed else defender.name
        self.events.append(f"Round {rnd}: {subj} {verb} a {punch.replace('_', ' ')}.")

    def _winner(self) -> str | None:
        r, b = self.red.name, self.blue.name
        return r if self.scores[r] > self.scores[b] else b if self.scores[b] > self.scores[r] else None
