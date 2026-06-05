from tabulate import tabulate

def print_results(items: list[str], prices: list[str]):
    rows = list(zip(items, prices))
    rows.sort(key=lambda x: x[1])  # sort by price
    print(tabulate(rows, headers=["Item", "Price"], tablefmt="rounded_outline"))


def print_result(item: str, price: str):
    print(f"   {item}: {price}")