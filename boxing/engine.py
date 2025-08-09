# boxing/engine.py
from __future__ import annotations

import random
from typing import List

from boxing.models import Boxer
from boxing.prob import block_score, dodge_score, parry_score

ROUNDS = 12
PUNCHES = ("jab", "straight", "lead_hook", "hook", "lead_uppercut", "uppercut")


class MatchEngine:
    """Runs a 12-round fight with Decision-based punch choice and land/evade logic."""

    # ------------------------------------------------------------------ #
    # Constructor                                                        #
    # ------------------------------------------------------------------ #
    def __init__(self, red: Boxer, blue: Boxer, *, seed: int | None = None):
        self.red, self.blue = red, blue
        self.rng = random.Random(seed)
        self.events: List[str] = []
        self.scores = {red.name: 0, blue.name: 0}

        # pre-compute punch-accuracy tables (0-to-1) for speed
        self.red_pacc = self._precompute_pacc(red)
        self.blue_pacc = self._precompute_pacc(blue)

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def simulate(self) -> dict:
        for rnd in range(1, ROUNDS + 1):
            self._simulate_round(rnd)
        return {"winner": self._winner(), "scores": self.scores, "events": self.events}

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _precompute_pacc(boxer: Boxer) -> dict[str, float]:
        """Avg(type-rating/20 , accuracy/20) for every punch once per fight."""
        acc = boxer.accuracy / 20
        return {p: ((getattr(boxer, p) / 20) + acc) / 2 for p in PUNCHES}

    # ------------------------------------------------------------------ #
    def _choose_punch(self, boxer: Boxer, table: dict[str, float]) -> str:
        """Decision-driven punch selection."""
        p_focus = boxer.decision / 20
        if self.rng.random() < p_focus:  # focused → pick highest-accuracy punch
            best = max(table.values())
            best_choices = [p for p, v in table.items() if v == best]
            return self.rng.choice(best_choices)
        # not focused → weighted random by punch accuracy
        weights = list(table.values())
        return self.rng.choices(list(table.keys()), weights=weights, k=1)[0]

    # ------------------------------------------------------------------ #
    def _simulate_round(self, rnd: int) -> None:
        red_landed = blue_landed = 0

        # two exchanges per round (simple demo logic)
        for _ in range(2):
            punch_r = self._choose_punch(self.red, self.red_pacc)
            punch_b = self._choose_punch(self.blue, self.blue_pacc)

            if self._throw(self.red, self.blue, punch_r, rnd):
                red_landed += 1
            if self._throw(self.blue, self.red, punch_b, rnd):
                blue_landed += 1

        # -------- 10-Point Must placeholder --------
        if red_landed > blue_landed:
            self.scores[self.red.name] += 10
            self.scores[self.blue.name] += 9
        elif blue_landed > red_landed:
            self.scores[self.blue.name] += 10
            self.scores[self.red.name] += 9
        else:
            self.scores[self.red.name] += 10
            self.scores[self.blue.name] += 10

    # ------------------------------------------------------------------ #
    def _throw(self, attacker: Boxer, defender: Boxer, punch: str, rnd: int) -> bool:
        # 1) punch accuracy (0-1)
        punch_acc = ((getattr(attacker, punch) / 20) + (attacker.accuracy / 20)) / 2

        # 2) defender’s three defence scores
        block = block_score(defender)
        dodge = dodge_score(defender)
        parry = parry_score(defender)

        # 3) Decision rule for which defence is attempted
        p_focus = defender.decision / 20
        if self.rng.random() < p_focus:
            chosen = max(block, dodge, parry)
        else:
            total = block + dodge + parry
            roll = self.rng.random()
            cutoff_block = block / total
            cutoff_dodge = cutoff_block + (dodge / total)
            chosen = block if roll < cutoff_block else dodge if roll < cutoff_dodge else parry

        # 4) land probability
        p_land = punch_acc / (punch_acc + chosen)
        landed = self.rng.random() < p_land

        # 5) narrative
        if landed:
            self.events.append(
                f"Round {rnd}: {attacker.name} lands a {punch.replace('_', ' ')}."
            )
        else:
            verb = "is blocked" if chosen == block else "misses"
            self.events.append(
                f"Round {rnd}: {attacker.name} {verb} a {punch.replace('_', ' ')}."
            )

        return landed

    # ------------------------------------------------------------------ #
    def _winner(self) -> str | None:
        r, b = self.red.name, self.blue.name
        return r if self.scores[r] > self.scores[b] else b if self.scores[b] > self.scores[r] else None
