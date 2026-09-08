import numpy as np


def simulate_freight_risk(
    current_rate,
    forecast_rate,
    volatility=0.6,
    cargo_quantity=50000,
    simulations=1000
):

    np.random.seed(42)

    simulated_rates = np.random.normal(
        loc=forecast_rate,
        scale=volatility,
        size=simulations
    )

    simulated_rates = np.maximum(simulated_rates, 5)

    current_freight_cost = current_rate * cargo_quantity

    simulated_costs = simulated_rates * cargo_quantity

    p10_rate = np.percentile(simulated_rates, 10)
    p50_rate = np.percentile(simulated_rates, 50)
    p90_rate = np.percentile(simulated_rates, 90)

    p10_cost = np.percentile(simulated_costs, 10)
    p50_cost = np.percentile(simulated_costs, 50)
    p90_cost = np.percentile(simulated_costs, 90)

    probability_wait_cheaper = np.mean(
        simulated_costs < current_freight_cost
    )

    return {
        "p10_rate": round(p10_rate, 2),
        "p50_rate": round(p50_rate, 2),
        "p90_rate": round(p90_rate, 2),
        "p10_cost": round(p10_cost, 2),
        "p50_cost": round(p50_cost, 2),
        "p90_cost": round(p90_cost, 2),
        "probability_wait_cheaper": round(
            probability_wait_cheaper * 100, 2
        )
    }


if __name__ == "__main__":

    result = simulate_freight_risk(
        current_rate=19.00,
        forecast_rate=18.96,
        volatility=0.6,
        cargo_quantity=50000,
        simulations=1000
    )

    print()
    print("FREIGHT RISK SIMULATION")
    print("=======================")

    for key, value in result.items():
        print(f"{key}: {value}")