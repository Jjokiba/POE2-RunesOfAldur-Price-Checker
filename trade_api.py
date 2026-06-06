import requests, os, json
import streamlit as st

LEAGUE    = "Runes%20of%20Aldur"   
    
def get_headers():
    POESESSID = st.secrets.get("POESESSID")

    return {
        "Cookie": f"POESESSID={POESESSID}",
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.pathofexile.com/trade2/search/poe2",
        "Content-Type": "application/json",
    }

def search_item(item_name: str) -> list[str]:
    """Returns a list of listing IDs for a given item name."""
    HEADERS = get_headers()

    url = f"https://www.pathofexile.com/api/trade2/search/poe2/{LEAGUE}"
    query = {
        "query": {
            "status": {
                "option": "available"
            },
            "type": f"{item_name}",
            "stats": [
                {
                    "type": "and",
                    "filters": []
                }
            ],
            "filters": {
                "trade_filters": {
                    "disabled": True,
                    "filters": {
                        "price": {
                            "option": "regal"
                        }
                    }
                }
            }
        },
        "sort": {
            "price": "asc"
        }
    }
    r = requests.post(url, data=json.dumps(query), headers=HEADERS)
    
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}")
    
    r.raise_for_status()

    return r.json().get("result", [])[:1]   # top 1 listings

def fetch_prices(listing_ids: list[str]) -> list[dict]:
    HEADERS = get_headers()
    """Fetches full listing data for a list of IDs."""
    ids_str = ",".join(listing_ids)
    url = f"https://www.pathofexile.com/api/trade2/fetch/{ids_str}"

    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()

    return r.json().get("result", [])

def get_price(item_name: str) -> str:
    """Returns a readable price string for an item."""
    ids = search_item(item_name)
    if not ids:
        return "No listings found"
    listings = fetch_prices(ids)
    if not listings:
        return "No price data"
    
    # Take the cheapest (already sorted asc)
    price_info = listings[0].get("listing", {}).get("price", {})
    amount    = price_info.get("amount", "?")
    currency  = price_info.get("currency", "?")

    return f"{amount} {currency}"

def get_item_data(item_name: str) -> dict:
    """Returns item data including price and currency icon URL from POE2 Wiki."""
    ids = search_item(item_name)
    if not ids:
        return {"price": "No listings found", "currency_icon": None, "quantity": 1}
    
    listings = fetch_prices(ids)
    if not listings:
        return {"price": "No price data", "currency_icon": None, "quantity": 1}
    
    listing = listings[0]
    
    # Get price
    price_info = listing.get("listing", {}).get("price", {})
    amount = price_info.get("amount", "?")
    currency = price_info.get("currency", "?")
    price = f"{amount} {currency}"
    
    # Map short API currency names to full currency names for wiki
    # Include both short and full names to handle API inconsistencies
    # All keys are lowercase to ensure proper lookup
    currency_name_map = {
        # Short names
        "augmentation": "Orb of Augmentation",
        "alteration": "Orb of Alteration",
        "transmutation": "Orb of Transmutation",
        "transmute": "Orb of Transmutation",
        "chance": "Orb of Chance",
        "fusing": "Orb of Fusing",
        "alchemy": "Orb of Alchemy",
        "binding": "Orb of Binding",
        "annulment": "Orb of Annulment",
        "chromatic": "Chromatic Orb",
        "jeweller": "Jeweller's Orb",
        "vaal": "Vaal Orb",
        "regal": "Regal Orb",
        "divine": "Divine Orb",
        "exalted": "Exalted Orb",
        "chaos": "Chaos Orb",
        "chisel": "Cartographer's Chisel",
        "wisdom": "Scroll of Wisdom",
        "portal": "Portal Scroll",
        "mirror": "Mirror of Kalandra",
        "exalted equivalent": "Exalted Orb Equivalent",
        "exalted or divine": "Exalted or Divine Orbs",
        # Full names (in case API returns full name) - all lowercase
        "orb of augmentation": "Orb of Augmentation",
        "orb of alteration": "Orb of Alteration",
        "orb of transmutation": "Orb of Transmutation",
        "orb of chance": "Orb of Chance",
        "orb of fusing": "Orb of Fusing",
        "orb of alchemy": "Orb of Alchemy",
        "orb of binding": "Orb of Binding",
        "orb of annulment": "Orb of Annulment",
        "chromatic orb": "Chromatic Orb",
        "jeweller's orb": "Jeweller's Orb",
        "vaal orb": "Vaal Orb",
        "regal orb": "Regal Orb",
        "divine orb": "Divine Orb",
        "exalted orb": "Exalted Orb",
        "chaos orb": "Chaos Orb",
        "cartographer's chisel": "Cartographer's Chisel",
        "scroll of wisdom": "Scroll of Wisdom",
        "portal scroll": "Portal Scroll",
        "mirror of kalandra": "Mirror of Kalandra",
        "exalted orb equivalent": "Exalted Orb Equivalent",
        "exalted or divine orbs": "Exalted or Divine Orbs",
    }
    
    # Get full currency name - strip whitespace and lowercase for lookup
    currency_clean = currency.strip().lower()
    full_currency_name = currency_name_map.get(currency_clean, currency_clean)
    
    # If we got back just the short name from the fallback, try to construct a full name
    # by capitalizing each word (this is a fallback for unmapped currencies)
    if full_currency_name == currency_clean:
        # Just in case it's not in the map, use title case as a reasonable default
        full_currency_name = currency_clean.replace("_", " ").title()
    
    # Get currency icon from POE2 Wiki Fextralife
    # Convert to wiki format: "Orb of Augmentation" -> "orb_of_augmentation"
    if currency != "?":
        currency_wiki = full_currency_name.lower().replace(" ", "_").replace("'", "")
        currency_icon = f"https://pathofexile2.wiki.fextralife.com/file/Path-of-Exile-2/{currency_wiki}_items_path_of_exile_2_wiki_guide_100px.png"
    else:
        currency_icon = None
    
    # Get item data (quantity and icon)
    item = listing.get("item", {})
    quantity = item.get("stackSize", 1)
    item_icon = item.get("icon", None)
    
    return {
        "price": price,
        "currency_icon": currency_icon,
        "quantity": quantity,
        "item_icon": item_icon
    }
