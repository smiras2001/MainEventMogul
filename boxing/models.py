from dataclasses import dataclass, field

SKILL_MIN, SKILL_MAX = 1, 20
SKILL_NAMES = ("jab", "hook", "uppercut", "straight", "dodge", "block")


@dataclass(slots=True, frozen=True)
class Boxer:
    """Immutable fighter blueprint."""

    name: str
    jab: int
    hook: int
    uppercut: int
    straight: int
    dodge: int
    block: int
    metadata: dict[str, str | int] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        skills = {k: getattr(self, k) for k in SKILL_NAMES}
        if not all(SKILL_MIN <= v <= SKILL_MAX for v in skills.values()):
            bad = {k: v for k, v in skills.items() if not SKILL_MIN <= v <= SKILL_MAX}
            raise ValueError(f"Skill ratings must be {SKILL_MIN}-{SKILL_MAX}. Offending: {bad}")