import sys, time
from ocr        import read_image
from parser     import parse_items
from trade_api  import get_price
from output     import print_result, print_results

def main(image_path: str):
    print(f"📷 Reading image: {image_path}")
    raw_text = read_image(image_path)

    print("🔍 Parsing item list...")
    items = parse_items(raw_text)
    print(f"   Found {len(items)} items: {items}\n")    

    prices = []
    for item in items:
        print(f"   Fetching price for: {item}")
        price = get_price(item)
        prices.append(price)
        print_result(item, price)
        time.sleep(2)   # rate-limit guard

    print("\n📊 Results:")
    print_results(items, prices)

if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else "items.png"
    main(image_path)
