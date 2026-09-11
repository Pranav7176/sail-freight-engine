import numpy as np


def evaluate_contract_strategy(
    cargo_quantity,
    current_rate,
    forecast,
    volatility
):
    forecast_rates = np.array(
        [item["forecast"] for item in forecast],
        dtype=float
    )

    average_30d_rate = float(np.mean(forecast_rates))

    min_rate = float(np.min(forecast_rates))
    max_rate = float(np.max(forecast_rates))

    spot_cost = cargo_quantity * current_rate

    short_term_voyages = 4
    medium_term_voyages = 8

    short_term_rate = (
        current_rate * 0.6 +
        average_30d_rate * 0.4
    )

    medium_term_rate = (
        current_rate * 0.4 +
        average_30d_rate * 0.6
    )

    short_term_rate += volatility * 0.15
    medium_term_rate += volatility * 0.30

    short_term_cost_per_voyage = (
        cargo_quantity * short_term_rate
    )

    medium_term_cost_per_voyage = (
        cargo_quantity * medium_term_rate
    )

    short_term_total = (
        short_term_cost_per_voyage *
        short_term_voyages
    )

    medium_term_total = (
        medium_term_cost_per_voyage *
        medium_term_voyages
    )

    spot_total = spot_cost

    short_term_saving = (
        spot_cost - short_term_cost_per_voyage
    )

    medium_term_saving = (
        spot_cost - medium_term_cost_per_voyage
    )

    forecast_change = (
        (average_30d_rate - current_rate)
        / current_rate
    ) * 100

    if forecast_change <= -3 and volatility <= 0.8:
        recommendation = "MEDIUM-TERM MULTIPLE VOYAGE"

        explanation = (
            "Forecast freight rates are lower than the "
            "current market with relatively controlled "
            "volatility. A medium-term multiple-voyage "
            "contract can capture the expected lower "
            "freight environment."
        )

    elif forecast_change <= 0:
        recommendation = "SHORT-TERM MULTIPLE VOYAGE"

        explanation = (
            "Forecast rates are stable or lower than the "
            "current market, but uncertainty does not "
            "justify a longer commitment. A short-term "
            "multiple-voyage contract balances savings "
            "with flexibility."
        )

    else:
        recommendation = "SPOT"

        explanation = (
            "Forecast freight rates are higher than the "
            "current market. Locking into a longer "
            "contract could reduce flexibility, so "
            "spot procurement is preferred."
        )

    return {
        "recommendation": recommendation,
        "current_rate": round(current_rate, 2),
        "average_30d_rate": round(average_30d_rate, 2),
        "forecast_change_percent": round(forecast_change, 2),
        "forecast_min": round(min_rate, 2),
        "forecast_max": round(max_rate, 2),
        "volatility": round(volatility, 2),
        "strategies": {
            "spot": {
                "voyages": 1,
                "rate_per_tonne": round(current_rate, 2),
                "cost_per_voyage": round(spot_cost, 2)
            },
            "short_term": {
                "voyages": short_term_voyages,
                "rate_per_tonne": round(
                    short_term_rate, 2
                ),
                "cost_per_voyage": round(
                    short_term_cost_per_voyage, 2
                ),
                "total_contract_cost": round(
                    short_term_total, 2
                ),
                "saving_per_voyage": round(
                    short_term_saving, 2
                )
            },
            "medium_term": {
                "voyages": medium_term_voyages,
                "rate_per_tonne": round(
                    medium_term_rate, 2
                ),
                "cost_per_voyage": round(
                    medium_term_cost_per_voyage, 2
                ),
                "total_contract_cost": round(
                    medium_term_total, 2
                ),
                "saving_per_voyage": round(
                    medium_term_saving, 2
                )
            }
        },
        "explanation": explanation
    }