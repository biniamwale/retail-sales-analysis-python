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




def analyze_sales_data(sales: pd.DataFrame) -> dict:
    """Analyzes sales data, generates charts, and calculates key metrics."""
    sales["month"] = sales["date"].dt.to_period("M").astype(str)
    sales["profit_margin"] = sales["profit"] / sales["revenue"]

    total_revenue = sales["revenue"].sum()
    total_profit = sales["profit"].sum()
    total_orders = sales["transaction_id"].nunique()
    average_order_value = total_revenue / total_orders
    profit_margin = total_profit / total_revenue

    monthly_sales = (
        sales.groupby("month", as_index=False)
        .agg(monthly_revenue=("revenue", "sum"), 
             monthly_profit=("profit", "sum"), 
             monthly_quantity=("quantity", "sum"))
        )
    
    category_sales = (
        sales.groupby("category", as_index=False)
        .agg(category_revenue=("revenue", "sum"), 
             category_profit=("profit", "sum"), 
             category_quantity=("quantity", "sum"))
        .sort_values("category_revenue", ascending=False)
        )
    
    product_sales = (
        sales.groupby("product", as_index=False)
        .agg(product_revenue=("revenue", "sum"), 
             product_quantity=("quantity", "sum"), 
             product_profit=("profit", "sum"))
        .sort_values("product_revenue", ascending=False)
        )
    
    city_sales = (
        sales.groupby("city", as_index=False)
        .agg(city_revenue=("revenue", "sum"), 
             city_profit=("profit", "sum"))
             .sort_values("city_revenue", ascending=False)
    )
    
    channel_sales = (
        sales.groupby("channel", as_index=False)
        .agg(channel_revenue=("revenue", "sum"), channel_profit=("profit", "sum"))
        .sort_values("channel_revenue", ascending=False)
    )

    # Chart 1: monthly revenue and profit
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly_sales["month"], monthly_sales["monthly_revenue"], marker="o", color="blue", label="Revenue")
    ax.plot(monthly_sales["month"], monthly_sales["monthly_profit"], marker="o", color="red", label="Profit")
    ax.set_xlabel("Month")
    ax.set_ylabel("ETB")
    ax.set_title("BiniMart: Monthly Revenue and Profit")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    save_chart(fig, "01_monthly_performance.png")

    # Chart 2: revenue and profit by category
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(category_sales))
    bar_width = 0.4
    ax.bar(x - bar_width / 2, category_sales["category_revenue"], width=bar_width, label="Revenue", color="blue")
    ax.bar(x + bar_width / 2, category_sales["category_profit"], width=bar_width, label="Profit", color="orange")
    ax.set_xticks(x)
    ax.set_xticklabels(category_sales["category"])
    ax.set_xlabel("Product category")
    ax.set_ylabel("ETB")
    ax.set_title("BiniMart: Revenue and Profit by Product Category")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    save_chart(fig, "02_category_performance.png")

    # Chart 3: top products
    top_products = product_sales.head(8)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top_products["product"], top_products["product_revenue"], color="yellowgreen")
    ax.set_xlabel("Revenue (ETB)")
    ax.set_title("BiniMart: Top 8 products by revenue")
    ax.grid(axis="x", alpha=0.25)
    save_chart(fig, "03_top_products.png")

    # Chart 4: city and sales channel share
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    axes[0].pie(city_sales["city_revenue"], labels=city_sales["city"], autopct="%1.1f%%")
    axes[0].set_title("BiniMart: Revenue share by city")
    axes[1].bar(channel_sales["channel"], channel_sales["channel_revenue"], color=["blue", "orange"])
    axes[1].set_title("BiniMart: Revenue by sales channel")
    axes[1].set_ylabel("Revenue (ETB)")
    axes[1].grid(axis="y", alpha=0.25)
    save_chart(fig, "04_city_and_channel.png")

    # Package metrics to pass to the report generator
    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "best_category": category_sales.iloc[0],
        "best_product": product_sales.iloc[0],
        "best_city": city_sales.iloc[0],
        "online_share": channel_sales.loc[channel_sales["channel"] == "Online", "channel_revenue"].iloc[0] / total_revenue,
        "best_month": monthly_sales.loc[monthly_sales["monthly_revenue"].idxmax()]
    }



def save_chart(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / name, dpi=180, bbox_inches="tight")
    plt.close(fig)




def generate_sales_report(metrics: dict) -> str:
    """Consumes the metrics dictionary to generate a Markdown report."""
    
    # Unpack metrics for cleaner f-string formatting
    total_revenue = metrics["total_revenue"]
    total_profit = metrics["total_profit"]
    profit_margin = metrics["profit_margin"]
    total_orders = metrics["total_orders"]
    average_order_value = metrics["average_order_value"]
    best_product = metrics["best_product"]
    best_category = metrics["best_category"]
    best_city = metrics["best_city"]
    best_month = metrics["best_month"]
    online_share = metrics["online_share"]

    report = f"""# BiniMart Sales Summary (2025)

**Period:** Jan 1, 2025 – Dec 31, 2025  
*(Internal Learning Project Data)*

---

### The Big Numbers

| What We Measured | Result |
|:---|---:|
| Total Sales (Revenue) | ETB {total_revenue:,.2f} |
| Total Profit | ETB {total_profit:,.2f} |
| Profit Margin | {profit_margin:.1%} |
| Total Orders Placed | {total_orders:,} |
| Average Spent per Order | ETB {average_order_value:,.2f} |

---

### What Worked Best

* **Top Product:** **{best_product['product']}** made **ETB {best_product['product_revenue']:,.2f}** ({int(best_product['product_quantity']):,} units sold).
* **Top Category:** **{best_category['category']}** brought in **ETB {best_category['category_revenue']:,.2f}**.
* **Top City:** Customers in **{best_city['city']}** bought the most (**ETB {best_city['city_revenue']:,.2f}**).
* **Best Month:** **{best_month['month']}** was your busiest month (**ETB {best_month['monthly_revenue']:,.2f}**).
* **Online Sales:** **{online_share:.1%}** of your total sales came from online orders.

---

### Next Steps to Make More Money

1. **Never run out of {best_product['product']}:** It is your biggest seller. Always reorder before stock gets low.
2. **Prepare early for {best_month['month']}:** Stock up and prepare deliveries before this rush hits so you do not miss sales.
3. **Double down online:** Since **{online_share:.1%}** of your revenue comes from the website, try offering product packages (bundles) to get buyers to spend more per checkout.
4. **Check profits before dropping slow products:** Even if an item sells less, it might have a high profit margin. Don't cut items until you verify their actual profit.
"""
    return report