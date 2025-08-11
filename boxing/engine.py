# boxing/engine.py
from __future__ import annotations

import random
from typing import List, Dict, Tuple

from boxing.models import Boxer
from boxing.prob import block_score, dodge_score, parry_score

ROUNDS = 12
PUNCHES = ("jab", "straight", "lead_hook", "hook", "lead_uppercut", "uppercut")
DEFENCES = ("block", "dodge", "parry")


class MatchEngine:
    """Runs a 12-round fight with Decision-driven punch choice and land/evade logic.
    Now records round-by-round telemetry: thrown/landed by type and defence usage.
    """

    def __init__(self, red: Boxer, blue: Boxer, *, seed: int | None = None):
        self.red, self.blue = red, blue
        self.rng = random.Random(seed)
        self.events: List[str] = []
        self.scores = {red.name: 0, blue.name: 0}
        self.rounds: List[Dict] = []  # telemetry

        # pre-compute punch-accuracy tables (0-to-1) for speed
        self.red_pacc = self._precompute_pacc(red)
        self.blue_pacc = self._precompute_pacc(blue)

    # ------------------------------ Public API ------------------------------ #
    def simulate(self) -> dict:
        for rnd in range(1, ROUNDS + 1):
            self._simulate_round(rnd)
        return {
            "winner": self._winner(),
            "scores": self.scores,
            "events": self.events,
            "rounds": self.rounds,  # ← telemetry
        }

    # ------------------------------ Helpers -------------------------------- #
    @staticmethod
    def _precompute_pacc(boxer: Boxer) -> dict[str, float]:
        """Avg(type-rating/20 , accuracy/20) for every punch once per fight."""
        acc = boxer.accuracy / 20
        return {p: ((getattr(boxer, p) / 20) + acc) / 2 for p in PUNCHES}

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

    def _empty_counts(self) -> Dict[str, int]:
        return {p: 0 for p in PUNCHES}

    def _empty_defence_counts(self) -> Dict[str, int]:
        return {d: 0 for d in DEFENCES}

    def _simulate_round(self, rnd: int) -> None:
        red_landed = blue_landed = 0

        # round telemetry container
        rsum = {
            "round": rnd,
            "red": {
                "thrown": self._empty_counts(),
                "landed": self._empty_counts(),
                "defence": self._empty_defence_counts(),
            },
            "blue": {
                "thrown": self._empty_counts(),
                "landed": self._empty_counts(),
                "defence": self._empty_defence_counts(),
            },
        }

        # two exchanges per round (simple demo logic)
        for _ in range(2):
            # Red attacks
            punch_r = self._choose_punch(self.red, self.red_pacc)
            rsum["red"]["thrown"][punch_r] += 1
            landed, defence_used = self._throw(self.red, self.blue, punch_r, rnd)
            rsum["blue"]["defence"][defence_used] += 1
            if landed:
                rsum["red"]["landed"][punch_r] += 1
                red_landed += 1

            # Blue attacks
            punch_b = self._choose_punch(self.blue, self.blue_pacc)
            rsum["blue"]["thrown"][punch_b] += 1
            landed, defence_used = self._throw(self.blue, self.red, punch_b, rnd)
            rsum["red"]["defence"][defence_used] += 1
            if landed:
                rsum["blue"]["landed"][punch_b] += 1
                blue_landed += 1

        # 10-Point Must placeholder (no damage/knockdowns yet)
        if red_landed > blue_landed:
            self.scores[self.red.name] += 10
            self.scores[self.blue.name] += 9
        elif blue_landed > red_landed:
            self.scores[self.blue.name] += 10
            self.scores[self.red.name] += 9
        else:
            self.scores[self.red.name] += 10
            self.scores[self.blue.name] += 10

        # stash telemetry
        self.rounds.append(rsum)

    def _throw(self, attacker: Boxer, defender: Boxer, punch: str, rnd: int) -> Tuple[bool, str]:
        """Return (landed, defence_used)."""
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

        # map chosen score back to a label
        if chosen == block:
            defence_used = "block"
        elif chosen == dodge:
            defence_used = "dodge"
        else:
            defence_used = "parry"

        # 4) land probability
        p_land = punch_acc / (punch_acc + chosen)
        landed = self.rng.random() < p_land

        # 5) narrative
        if landed:
            self.events.append(
                f"Round {rnd}: {attacker.name} lands a {punch.replace('_', ' ')}."
            )
        else:
            verb = "blocked" if defence_used == "block" else "misses"
            self.events.append(
                f"Round {rnd}: {attacker.name} {verb} a {punch.replace('_', ' ')}."
            )

        return landed, defence_used

    def _winner(self) -> str | None:
        r, b = self.red.name, self.blue.name
        return r if self.scores[r] > self.scores[b] else b if self.scores[b] > self.scores[r] else None
