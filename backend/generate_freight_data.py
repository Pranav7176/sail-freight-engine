import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")
FREIGHT_FILE = DATA_DIR / "freight.csv"

origins = [
    "Australia",
    "USA",
    "Mozambique",
    "Indonesia",
    "Russia"
]

destinations = [
    "Dhamra",
    "Paradip",
    "Visakhapatnam",
    "Gangavaram",
    "Gopalpur",
    "Sagar-Sandheads",
    "Haldia"
]

vessel_classes = [
    "Handysize",
    "Panamax",
    "Supramax",
    "Capesize"
]

vessel_base_rates = {
    "Handysize": 21.0,
    "Panamax": 19.0,
    "Supramax": 20.2,
    "Capesize": 17.8
}

origin_factors = {
    "Australia": 1.00,
    "USA": 1.65,
    "Mozambique": 1.25,
    "Indonesia": 0.88,
    "Russia": 1.45
}

destination_factors = {
    "Dhamra": 1.00,
    "Paradip": 1.08,
    "Visakhapatnam": 1.04,
    "Gangavaram": 0.94,
    "Gopalpur": 1.07,
    "Sagar-Sandheads": 1.14,
    "Haldia": 1.17
}

np.random.seed(42)

existing = pd.read_csv(FREIGHT_FILE)
existing["date"] = pd.to_datetime(
    existing["date"],
    format="mixed"
)

existing_route = existing[
    (existing["origin"] == "Australia") &
    (existing["destination"] == "Dhamra")
].copy()

dates = sorted(existing_route["date"].unique())

new_rows = []

for origin in origins:
    for destination in destinations:

        if origin == "Australia" and destination == "Dhamra":
            continue

        for vessel_class in vessel_classes:

            base_rate = (
                vessel_base_rates[vessel_class]
                * origin_factors[origin]
                * destination_factors[destination]
            )

            previous_rate = base_rate

            for date in dates:

                seasonal = (
                    0.45 * np.sin(
                        2 * np.pi * date.timetuple().tm_yday / 365
                    )
                )

                weekly = (
                    0.18 * np.sin(
                        2 * np.pi * date.weekday() / 7
                    )
                )

                market_shock = np.random.normal(0, 0.45)

                rate = (
                    0.70 * previous_rate
                    + 0.30 * base_rate
                    + seasonal
                    + weekly
                    + market_shock
                )

                rate = max(rate, 5.0)

                new_rows.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "origin": origin,
                    "destination": destination,
                    "vessel_class": vessel_class,
                    "freight_rate": round(rate, 2)
                })

                previous_rate = rate

new_data = pd.DataFrame(new_rows)

final_data = pd.concat(
    [existing_route, new_data],
    ignore_index=True
)

final_data = final_data.sort_values(
    ["origin", "destination", "vessel_class", "date"]
).reset_index(drop=True)

final_data.to_csv(
    FREIGHT_FILE,
    index=False
)

print()
print("FREIGHT DATASET UPDATED")
print("=======================")
print(f"Total rows: {len(final_data)}")
print()

print("Rows by origin:")
print(final_data["origin"].value_counts())

print()
print("Rows by vessel class:")
print(final_data["vessel_class"].value_counts())

print()
print("Rows by route:")
print(
    final_data
    .groupby(["origin", "destination"])
    .size()
)

print()
print(f"Saved to: {FREIGHT_FILE}")