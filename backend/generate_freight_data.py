import pandas as pd
import numpy as np

np.random.seed(42)

dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")

vessel_classes = {
    "Panamax": 18.0,
    "Supramax": 20.0,
    "Capesize": 16.0
}

rows = []

for vessel_class, base_rate in vessel_classes.items():

    for i, date in enumerate(dates):

        trend = 0.003 * i

        seasonal = 1.5 * np.sin(2 * np.pi * i / 365)

        weekly = 0.4 * np.sin(2 * np.pi * i / 7)

        volatility = np.random.normal(0, 0.6)

        freight_rate = (
            base_rate
            + trend
            + seasonal
            + weekly
            + volatility
        )

        freight_rate = max(freight_rate, 5)

        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "origin": "Australia",
            "destination": "Dhamra",
            "vessel_class": vessel_class,
            "freight_rate": round(freight_rate, 2)
        })

df = pd.DataFrame(rows)

df.to_csv("data/freight.csv", index=False)

print("Freight dataset created successfully.")
print(f"Rows: {len(df)}")
print()
print(df.head())