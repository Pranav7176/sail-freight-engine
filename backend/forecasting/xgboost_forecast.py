import pandas as pd
import numpy as np
from xgboost import XGBRegressor


def create_features(df):

    df = df.copy()

    df["lag_1"] = df["freight_rate"].shift(1)
    df["lag_2"] = df["freight_rate"].shift(2)
    df["lag_3"] = df["freight_rate"].shift(3)
    df["lag_7"] = df["freight_rate"].shift(7)

    df["rolling_7"] = df["freight_rate"].rolling(7).mean()
    df["rolling_14"] = df["freight_rate"].rolling(14).mean()

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_year"] = df["date"].dt.dayofyear

    return df


def train_model(vessel_class="Panamax"):

    df = pd.read_csv("data/freight.csv")

    df = df[df["vessel_class"] == vessel_class].copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    training_data = create_features(df).dropna()

    features = [
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_7",
        "rolling_7",
        "rolling_14",
        "day_of_week",
        "day_of_year"
    ]

    X = training_data[features]
    y = training_data["freight_rate"]

    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42
    )

    model.fit(X, y)

    return model, df, features


def forecast_future(vessel_class="Panamax", days=30):

    model, df, features = train_model(vessel_class)

    history = list(df["freight_rate"])

    last_date = df["date"].iloc[-1]

    forecasts = []

    for i in range(1, days + 1):

        current_date = last_date + pd.Timedelta(days=i)

        lag_1 = history[-1]
        lag_2 = history[-2]
        lag_3 = history[-3]
        lag_7 = history[-7]

        rolling_7 = np.mean(history[-7:])
        rolling_14 = np.mean(history[-14:])

        day_of_week = current_date.dayofweek
        day_of_year = current_date.dayofyear

        X_future = pd.DataFrame([[
            lag_1,
            lag_2,
            lag_3,
            lag_7,
            rolling_7,
            rolling_14,
            day_of_week,
            day_of_year
        ]], columns=features)

        prediction = float(model.predict(X_future)[0])
        prediction = max(prediction, 5)

        history.append(prediction)

        forecasts.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "forecast": round(prediction, 2)
        })

    return forecasts


if __name__ == "__main__":

    forecast = forecast_future(
        vessel_class="Panamax",
        days=30
    )

    print()
    print("PANAMAX FREIGHT FORECAST")
    print("========================")

    for row in forecast:
        print(row)