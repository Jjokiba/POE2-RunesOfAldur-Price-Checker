import streamlit as st

def parse_items(raw_text: str) -> list[str]:
    lines = raw_text.splitlines()
    items = []
    
    for line in lines:
        cleaned = line.strip()
        if cleaned:                    # skip blank lines
            items.append(cleaned)   

    items = [
        item
        for item in items
        if (
            item.upper() not in ("IX", "1X")
            and "unique" not in item.lower()
            and "rueshape" not in item.lower()
            and "runeshape" not in item.lower()
        )
    ]
    items = [
        item.lower().replace("ix ", "").replace("1x ", "").replace("support:", "").replace("skill:", "").strip().title()
        for item in items
    ]

    for item in items:
        st.info(f"Parsed item: {item}") 

    return items

# Example output:
# ["Thaumaturgic Flux (Level 12)", "Warding Rune of Reinforcement", "Greater Charging Rune", "Greater Ward Rune", "Chaos Orb",  "Exalted Orb", "Orb of Alteration", "Divine Orb"]
