import pandas as pd
import os
import shutil

CURRENT_FILE = "data/freight_current.csv"
HISTORICAL_FILE = "data/freight.csv"
BACKUP_FILE = "data/freight_current_backup.csv"

ORIGINS = [
    "Australia",
    "USA",
    "Mozambique",
    "Russia",
    "Indonesia"
]

DESTINATIONS = [
    "Dhamra",
    "Paradip",
    "Visakhapatnam",
    "Gangavaram",
    "Gopalpur",
    "Sagar-Sandheads",
    "Haldia"
]

VESSEL_CLASSES = [
    "Capesize",
    "Panamax",
    "Supramax",
    "Handysize"
]

print("Loading freight data...")

current = pd.read_csv(CURRENT_FILE)
historical = pd.read_csv(HISTORICAL_FILE)

if not os.path.exists(BACKUP_FILE):
    shutil.copy2(CURRENT_FILE, BACKUP_FILE)
    print("Backup created:", BACKUP_FILE)

historical["date"] = pd.to_datetime(historical["date"])

latest = (
    historical
    .sort_values("date")
    .groupby(
        ["origin", "destination", "vessel_class"],
        as_index=False
    )
    .tail(1)
)

latest = latest[
    ["origin", "destination", "vessel_class", "freight_rate"]
].rename(
    columns={"freight_rate": "current_rate"}
)

required = pd.MultiIndex.from_product(
    [ORIGINS, DESTINATIONS, VESSEL_CLASSES],
    names=["origin", "destination", "vessel_class"]
).to_frame(index=False)

current_keys = current[
    ["origin", "destination", "vessel_class"]
].drop_duplicates()

missing = required.merge(
    current_keys,
    on=["origin", "destination", "vessel_class"],
    how="left",
    indicator=True
)

missing = missing[missing["_merge"] == "left_only"].drop(
    columns="_merge"
)

print(f"Existing current-rate combinations: {len(current_keys)}")
print(f"Missing combinations: {len(missing)}")

if len(missing) > 0:

    additions = missing.merge(
        latest,
        on=["origin", "destination", "vessel_class"],
        how="left"
    )

    unresolved = additions[additions["current_rate"].isna()]

    if not unresolved.empty:
        print("\nERROR: Historical data is missing these combinations:")
        print(unresolved.to_string(index=False))
        raise SystemExit(1)

    current = pd.concat(
        [current, additions],
        ignore_index=True
    )

current = (
    current[
        ["origin", "destination", "vessel_class", "current_rate"]
    ]
    .drop_duplicates(
        subset=["origin", "destination", "vessel_class"],
        keep="last"
    )
)

current.to_csv(CURRENT_FILE, index=False)

print("\nDone.")
print(f"Total current-rate combinations: {len(current)}")

expected = len(ORIGINS) * len(DESTINATIONS) * len(VESSEL_CLASSES)

if len(current) == expected:
    print(f"SUCCESS: All {expected} combinations are present.")
else:
    print(
        f"WARNING: Expected {expected}, "
        f"but found {len(current)}."
    )

print("\nRoute coverage:")

coverage = (
    current
    .groupby(["origin", "destination"])
    .size()
    .reset_index(name="vessel_classes")
)

print(coverage.to_string(index=False))