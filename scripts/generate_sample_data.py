"""Generate deterministic sample sales data for TrendPilot."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


RANDOM_SEED = 20260715
START_DATE = date(2026, 4, 1)
DAYS = 90
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_sales_data.csv"

PRODUCTS = [
    ("P001", "黑色冲锋衣", "冲锋衣", 699.0, 285.0, 780),
    ("P002", "云白防晒衣", "防晒衣", 399.0, 148.0, 1050),
    ("P003", "卡其工装裤", "工装裤", 459.0, 176.0, 920),
    ("P004", "灰色连帽卫衣", "卫衣", 329.0, 122.0, 1150),
    ("P005", "复古印花T恤", "T恤", 199.0, 63.0, 1380),
    ("P006", "轻量羽绒服", "羽绒服", 899.0, 382.0, 680),
    ("P007", "水洗牛仔裤", "牛仔裤", 429.0, 168.0, 990),
    ("P008", "机能运动鞋", "运动鞋", 599.0, 236.0, 860),
    ("P009", "城市斜挎包", "斜挎包", 289.0, 96.0, 1240),
    ("P010", "刺绣棒球帽", "棒球帽", 159.0, 48.0, 1460),
]


def generate_sample_data() -> pd.DataFrame:
    """Return 90 days of reproducible daily operating data for 10 products."""
    rng = random.Random(RANDOM_SEED)
    inventory_by_product = {product[0]: product[5] for product in PRODUCTS}
    rows: list[dict[str, object]] = []

    for day_index in range(DAYS):
        current_date = START_DATE + timedelta(days=day_index)
        weekend_factor = 1.15 if current_date.weekday() >= 5 else 1.0
        campaign_factor = 1.28 if 38 <= day_index <= 44 else 1.0

        for product_index, (product_id, name, category, price, cost, _) in enumerate(PRODUCTS):
            popularity = 0.82 + product_index * 0.045
            impressions = int(rng.randint(2600, 5200) * popularity * weekend_factor * campaign_factor)
            click_rate = rng.uniform(0.055, 0.105)
            product_clicks = max(1, int(impressions * click_rate))
            visitors = max(product_clicks, int(product_clicks * rng.uniform(1.15, 1.55)))
            add_to_cart = int(product_clicks * rng.uniform(0.16, 0.30))
            orders = min(add_to_cart, int(visitors * rng.uniform(0.025, 0.060)))
            units_sold = orders + rng.randint(0, max(1, orders // 5))

            if day_index in (29, 59):
                inventory_by_product[product_id] += 600 + product_index * 40
            inventory_by_product[product_id] = max(
                0, inventory_by_product[product_id] - units_sold
            )

            effective_price = price * rng.uniform(0.91, 0.99)
            sales_amount = round(units_sold * effective_price, 2)
            ad_spend = round(sales_amount / rng.uniform(3.2, 6.8), 2)
            refund_units = rng.randint(0, min(2, units_sold)) if units_sold else 0
            rating = round(min(5.0, max(4.0, rng.gauss(4.55, 0.18))), 1)

            rows.append(
                {
                    "date": current_date.isoformat(),
                    "product_id": product_id,
                    "product_name": name,
                    "category": category,
                    "price": price,
                    "cost": cost,
                    "impressions": impressions,
                    "visitors": visitors,
                    "product_clicks": product_clicks,
                    "add_to_cart": add_to_cart,
                    "orders": orders,
                    "units_sold": units_sold,
                    "sales_amount": sales_amount,
                    "ad_spend": ad_spend,
                    "refund_units": refund_units,
                    "inventory": inventory_by_product[product_id],
                    "rating": rating,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    dataframe = generate_sample_data()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(
        f"Generated {len(dataframe)} rows for "
        f"{dataframe['product_id'].nunique()} products at {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
