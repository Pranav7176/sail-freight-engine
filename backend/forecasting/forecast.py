import pandas as pd


def naive_forecast(vessel_class="Panamax", days=7):

    df = pd.read_csv("data/freight.csv")

    df = df[df["vessel_class"] == vessel_class]

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date")

    last_rate = df.iloc[-1]["freight_rate"]

    last_date = df.iloc[-1]["date"]

    forecasts = []

    for i in range(1, days + 1):

        forecast_date = last_date + pd.Timedelta(days=i)

        forecasts.append({
            "date": forecast_date.strftime("%Y-%m-%d"),
            "forecast": round(last_rate, 2)
        })

    return forecasts


if __name__ == "__main__":

    result = naive_forecast(
        vessel_class="Panamax",
        days=7
    )

    for row in result:
        print(row)