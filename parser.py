def parse_items(raw_text: str) -> list[str]:
    lines = raw_text.splitlines()
    items = []
    
    for line in lines:
        cleaned = line.strip()
        if cleaned:                    # skip blank lines
            items.append(cleaned)

    items.remove("Rueshape Cowbinatidws")
    items = [
        item
        for item in items
        if (
            item.upper() not in ("IX", "1X")
            and "unique" not in item.lower()
            and "Rueshape" not in item.lower()
            and "Runeshape" not in item.lower()
        )
    ]
    items = [
        item.replace("Ix ", "").replace("1x ", "").strip()
        for item in items
    ]

    return items

# Example output:
# ["Thaumaturgic Flux (Level 12)", "Warding Rune of Reinforcement", "Greater Charging Rune", "Greater Ward Rune", "Chaos Orb",  "Exalted Orb", "Orb of Alteration", "Divine Orb"]
