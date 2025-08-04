def hit(accuracy: int, defender_block: int, defender_reflexes: int, rng) -> bool:
    """
    Return True if punch lands, False otherwise.

    P(hit) = accuracy / (accuracy + max(block, reflexes))
    """
    chance = accuracy / (accuracy + max(defender_block, defender_reflexes))
    return rng.random() < chance
