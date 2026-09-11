import pandas as pd


def get_current_rate(origin, destination, vessel_class):

    freight = pd.read_csv("data/freight_current.csv")

    result = freight[
        (freight["origin"] == origin) &
        (freight["destination"] == destination) &
        (freight["vessel_class"] == vessel_class)
    ]

    if result.empty:
        return None

    return float(result.iloc[0]["current_rate"])