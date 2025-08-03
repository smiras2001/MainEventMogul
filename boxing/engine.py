from __future__ import annotations

import random
from typing import List

from .models import Boxer

ROUNDS = 12
SECONDS_PER_ROUND = 180


class MatchEngine:
    """Runs a full fight between two boxers."""

    def __init__(self, red: Boxer, blue: Boxer, *, seed: int | None = None):
        self.red, self.blue = red, blue
        self.rng = random.Random(seed)
        self.events: List[str] = []
        self.scores: dict[str, int] = {red.name: 0, blue.name: 0}

    # --- public API ---------------------------------------------------------

    def simulate(self) -> dict:
        """Return fight summary dict with winner, events list, and scorecards."""
        for rnd in range(1, ROUNDS + 1):
            self._simulate_round(rnd)
        winner = self._decide_winner()
        return {"winner": winner, "events": self.events, "scores": self.scores}

    # --- internal helpers ---------------------------------------------------

    def _simulate_round(self, rnd: int) -> None:
        # placeholder: one jab each so we can test plumbing
        self.events.append(f"Round {rnd}: {self.red.name} jabs at {self.blue.name}.")
        self.events.append(f"Round {rnd}: {self.blue.name} jabs back.")
        # temporary 10-10 scoring
        self.scores[self.red.name] += 10
        self.scores[self.blue.name] += 10

    def _decide_winner(self) -> str | None:
        r, b = self.red.name, self.blue.name
        if self.scores[r] > self.scores[b]:
            return r
        if self.scores[b] > self.scores[r]:
            return b
        return None  # draw
