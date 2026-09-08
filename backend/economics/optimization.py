def compare_charter_timing(
    cargo_quantity,
    current_rate,
    forecast_7,
    forecast_14,
    base_cost
):

    current_cost = base_cost

    rate_difference_7 = forecast_7 - current_rate
    rate_difference_14 = forecast_14 - current_rate

    cost_7 = base_cost + (
        rate_difference_7 * cargo_quantity
    )

    cost_14 = base_cost + (
        rate_difference_14 * cargo_quantity
    )

    options = {
        "charter_now": round(current_cost, 2),
        "wait_7_days": round(cost_7, 2),
        "wait_14_days": round(cost_14, 2)
    }

    best_option = min(options, key=options.get)

    return options, best_option


if __name__ == "__main__":

    cargo_quantity = 50000

    current_rate = 19.00
    forecast_7 = 19.00
    forecast_14 = 18.96

    base_cost = 1239859.15

    options, best = compare_charter_timing(
        cargo_quantity,
        current_rate,
        forecast_7,
        forecast_14,
        base_cost
    )

    print()
    print("CHARTER TIMING OPTIMIZER")
    print("========================")

    for option, cost in options.items():
        print(f"{option}: ${cost:,.2f}")

    print()
    print("BEST OPTION:", best.upper())