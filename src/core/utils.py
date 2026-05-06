def mask_plate(plate: str) -> str:
    """Return a log-safe plate string showing only the last 2 digits."""
    return "****" + plate[-2:] if len(plate) >= 2 else "****"
