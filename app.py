from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).parent / "results"
DATA_PATH = OUTPUT_DIR / "fictional_store_sales.csv"
RNG = np.random.default_rng(42)  # fixed seed: the fictional data is reproducible


def create_sales_data() -> pd.DataFrame:
    """Create one year of fictional transactions for BiniMart, a small retail store."""
    products = {
        "Electronics": [("Wireless Earbuds", 45, 25), ("Smart Watch", 80, 48), ("Phone Charger", 18, 7), ("Tablet", 200, 120), ("Bluetooth Speaker", 60, 35), ("Laptop", 1200, 500), ("Smartphone", 600, 350)],
        "Home": [("Desk Lamp", 30, 14), ("Storage Box", 15, 6), ("Water Bottle", 12, 4), ("Vacuum Cleaner", 150, 80), ("Coffee Maker", 90, 45)],
        "Fashion": [("T-Shirt", 20, 8), ("Hoodie", 42, 20), ("Sneakers", 65, 37), ("Jeans", 50, 25), ("Jacket", 90, 45)],
        "Beauty": [("Face Cream", 24, 10), ("Shampoo", 11, 4), ("Perfume", 55, 28), ("Makeup Kit", 70, 35), ("Hair Dryer", 40, 20)],
    }
    cities = ["Addis Ababa","Dubai", "Nairobi", "Bahir Dar", "Hawassa"]
    city_weights = [0.35, 0.28, 0.13, 0.17, 0.07]
    channels = ["Online", "Store"]
    channel_weights = [0.58, 0.42]
    sales_rows = []
    transaction_number = 10001

    # More sales around November/December to imitate holiday demand.
    for date in pd.date_range("2025-01-01", "2025-12-31", freq="D"):
        daily_sales = int(RNG.integers(8, 18))
        if date.month in (11, 12):
            daily_sales += int(RNG.integers(5, 13))
        if date.weekday() >= 5:
            daily_sales += int(RNG.integers(1, 6))

        for _ in range(daily_sales):
            category = RNG.choice(list(products.keys()))
            product, price, cost = products[category][RNG.integers(len(products[category]))]
            quantity = int(RNG.choice([1, 2, 3, 4], p=[0.60, 0.26, 0.10, 0.04]))

            #Discount rate based on price range.
            if price < 30:
                discount_rate = 0.02   # 2%
            elif price < 100:
                discount_rate = 0.05   # 5%
            elif price < 300:
                discount_rate = 0.08   # 8%
            else:
                discount_rate = 0.10   # 10%

            # +- 2.5% random variation in selling price just like in real life.
            unit_price = price * (1 + RNG.normal(0, 0.025))

            revenue = unit_price * quantity * (1 - discount_rate)
            profit = revenue - cost * quantity

            sales_rows.append({
                "transaction_id": f"BM-{transaction_number}",
                "date": date,
                "city": RNG.choice(cities, p=city_weights),
                "channel": RNG.choice(channels, p=channel_weights),
                "category": category,
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_rate": discount_rate,
                "revenue": revenue,
                "cost": round(cost * quantity, 2),
                "profit": profit,
            })
            transaction_number += 1

    return pd.DataFrame(sales_rows)


