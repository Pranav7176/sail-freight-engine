import pandas as pd
import numpy as np

def evaluate_naive(vessel_class="Panamax", test_days=30):

    df = pd.read_csv("data/freight.csv")

    df = df[df["vessel_class"] == vessel_class].copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    train = df.iloc[:-test_days]
    test = df.iloc[-test_days:]

    predictions = []

    last_rate = train.iloc[-1]["freight_rate"]

    for _ in range(test_days):
        predictions.append(last_rate)

    actual = test["freight_rate"].values
    predicted = np.array(predictions)

    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    print("Vessel Class:", vessel_class)
    print("Test Days:", test_days)
    print()
    print("Naive Baseline Results")
    print("----------------------")
    print("MAE :", round(mae, 3))
    print("RMSE:", round(rmse, 3))

if __name__ == "__main__":
    evaluate_naive()