from boxing.models import Boxer
# ---------------------------------------------------------------------------
# Defence scores (0-to-1 fractions) – used by the match engine
# ---------------------------------------------------------------------------
def block_score(b: Boxer) -> float:
    """Pure guard: blocking / 20."""
    return b.blocking / 20


def dodge_score(b: Boxer) -> float:
    """
    Dodge = avg(
        reflexes / 20 ,
        avg( anticipation / 20 , agility / 20 )
    )
    """
    part1 = b.reflexes / 20
    part2 = (b.anticipation / 20 + b.agility / 20) / 2
    return (part1 + part2) / 2


def parry_score(b: Boxer) -> float:
    """
    Parry = avg(
        blocking / 20 ,
        avg( anticipation / 20 , composure / 20 ) ,
        avg( reflexes / 20 , agility / 20 )
    )
    """
    block_part = b.blocking / 20
    hand_read  = (b.anticipation / 20 + b.composure / 20) / 2
    hand_speed = (b.reflexes / 20 + b.agility / 20) / 2
    return (block_part + hand_read + hand_speed) / 3

