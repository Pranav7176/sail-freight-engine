from economics.voyage_cost import calculate_voyage_cost


def run_scenario(
    cargo_quantity,
    freight_rate,
    distance_nm,
    vessel_speed,
    fuel_price,
    fuel_consumption,
    port_cost,
    waiting_days,
    demurrage_per_day
):
    return calculate_voyage_cost(
        cargo_quantity,
        freight_rate,
        distance_nm,
        vessel_speed,
        fuel_price,
        fuel_consumption,
        port_cost,
        waiting_days,
        demurrage_per_day
    )


def compare_scenarios(baseline, scenario):
    difference = scenario["total_cost"] - baseline["total_cost"]

    percentage = (
        difference / baseline["total_cost"]
    ) * 100

    return {
        "cost_difference": round(difference, 2),
        "percentage_change": round(percentage, 2)
    }


if __name__ == "__main__":

    baseline = run_scenario(
        50000, 19.00, 3000, 14.5,
        600, 35, 75000, 1.2, 25000
    )

    stressed = run_scenario(
        50000, 19.00, 3000, 14.5,
        800, 35, 75000, 3.0, 25000
    )

    comparison = compare_scenarios(
        baseline,
        stressed
    )

    print()
    print("SCENARIO SIMULATOR")
    print("==================")

    print()
    print("BASELINE")
    print("--------")
    print(f"Total Cost: ${baseline['total_cost']:,.2f}")
    print(f"Cost/Tonne: ${baseline['cost_per_tonne']:.2f}")

    print()
    print("STRESSED SCENARIO")
    print("-----------------")
    print("Bunker Price: $800")
    print("Waiting Days: 3.0")

    print(f"Total Cost: ${stressed['total_cost']:,.2f}")
    print(f"Cost/Tonne: ${stressed['cost_per_tonne']:.2f}")

    print()
    print("IMPACT")
    print("------")
    print(
        f"Cost Increase: "
        f"${comparison['cost_difference']:,.2f}"
    )
    print(
        f"Percentage Increase: "
        f"{comparison['percentage_change']:.2f}%"
    )