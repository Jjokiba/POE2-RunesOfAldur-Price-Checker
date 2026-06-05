import requests, os, json
from dotenv import load_dotenv

load_dotenv()
POESESSID = os.getenv("POESESSID")
LEAGUE    = "Runes%20of%20Aldur"   
HEADERS   = {
    "Cookie": f"POESESSID={POESESSID}",
    "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.pathofexile.com/trade2/search/poe2",
    "Content-Type": "application/json",
}

def search_item(item_name: str) -> list[str]:
    """Returns a list of listing IDs for a given item name."""
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
