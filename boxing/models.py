from dataclasses import dataclass, field

SKILL_MIN, SKILL_MAX = 1, 20
SKILL_NAMES = (
    # fundamentals
    "jab",
    "straight",
    "lead_hook",
    "hook",
    "lead_uppercut",
    "uppercut",
    "block",
    "accuracy",
    # athleticism
    "power",
    "reflexes",
)


@dataclass(slots=True, frozen=True)
class Boxer:
    """Immutable fighter blueprint (ratings 1-20)."""

    name: str
    jab: int
    straight: int
    lead_hook: int
    hook: int
    lead_uppercut: int
    uppercut: int
    block: int
    accuracy: int
    power: int
    reflexes: int
    metadata: dict = field(default_factory=dict, repr=False)

    def __post_init__(self):
        bad = {
            k: getattr(self, k)
            for k in SKILL_NAMES
            if not SKILL_MIN <= getattr(self, k) <= SKILL_MAX
        }
        if bad:
            raise ValueError(
                f"Ratings must be {SKILL_MIN}-{SKILL_MAX}. Offending: {bad}"
            )
