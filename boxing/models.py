from dataclasses import dataclass, field

SKILL_MIN, SKILL_MAX = 1, 20

@dataclass(slots=True, frozen=True)
class Boxer:
    # Fundamentals
    jab: int; straight: int; lead_hook: int; hook: int
    lead_uppercut: int; uppercut: int; blocking: int; accuracy: int
    # Boxing IQ
    anticipation: int; composure: int; positioning: int; decision: int
    aggression: int; focus: int; workrate: int; planning: int
    # Athleticism
    power: int; hand_speed: int; foot_speed: int
    reflexes: int; stamina: int; agility: int
    # Meta
    name: str = "Unnamed"

    def __post_init__(self):
        bad = {
            k: getattr(self, k)
            for k in self.__annotations__  # <-- instead of self.__dict__
            if isinstance(getattr(self, k), int) and not (1 <= getattr(self, k) <= 20)
        }
        if bad:
            raise ValueError(f"Ratings must be 1–20. Offenders: {bad}")

    # --- derived defence helpers (0-1 fractions) --------------------------
    def block_score(self) -> float:
        return self.blocking / 20

    def dodge_score(self) -> float:
        part1 = self.reflexes / 20
        part2 = (self.anticipation / 20 + self.agility / 20) / 2
        return (part1 + part2) / 2

    def parry_score(self) -> float:
        block_part = self.blocking / 20
        hand_read = (self.anticipation / 20 + self.composure / 20) / 2
        hand_speed = (self.reflexes / 20 + self.agility / 20) / 2
        return (block_part + hand_read + hand_speed) / 3