import pandas as pd

from vessel_engine import find_feasible_vessels
from economics.voyage_cost import calculate_voyage_cost
from forecasting.xgboost_forecast import forecast_future
from risk_engine import simulate_freight_risk


def run_decision_engine():

    cargo_quantity = 50000
    destination = "Dhamra"
    vessel_class = "Panamax"

    current_rate = 19.00

    distance_nm = 3000
    fuel_price = 600
    fuel_consumption = 35
    port_cost = 75000
    demurrage_per_day = 25000

    print()
    print("========================================")
    print("     SAIL FREIGHT DECISION ENGINE")
    print("========================================")

    print()
    print("CARGO REQUIREMENT")
    print("-----------------")
    print(f"Cargo: {cargo_quantity:,} tonnes")
    print("Origin: Australia")
    print(f"Destination: {destination}")
    print(f"Vessel Class: {vessel_class}")

    print()
    print("1. VESSEL-PORT FEASIBILITY")
    print("---------------------------")

    feasible_vessels = find_feasible_vessels(
        cargo_quantity=cargo_quantity,
        destination=destination
    )

    feasible = [
        vessel for vessel in feasible_vessels
        if vessel["status"] == "FEASIBLE"
        and vessel["class"] == vessel_class
    ]

    for vessel in feasible_vessels:
        print(
            f"{vessel['vessel']}: "
            f"{vessel['status']}"
        )

    if not feasible:
        print()
        print("No feasible vessels found.")
        return

    print()
    print(f"Feasible {vessel_class} vessels: {len(feasible)}")

    print()
    print("2. FREIGHT FORECAST")
    print("-------------------")

    forecasts = forecast_future(
        vessel_class=vessel_class,
        days=30
    )

    forecast_7 = float(forecasts[6]["forecast"])
    forecast_14 = float(forecasts[13]["forecast"])
    forecast_30 = float(forecasts[29]["forecast"])

    print(f"Current: ${current_rate:.2f}/tonne")
    print(f"7-Day:   ${forecast_7:.2f}/tonne")
    print(f"14-Day:  ${forecast_14:.2f}/tonne")
    print(f"30-Day:  ${forecast_30:.2f}/tonne")

    print()
    print("3. VOYAGE ECONOMICS")
    print("-------------------")

    # vessel = feasible[0]

    # voyage = calculate_voyage_cost(
    #     cargo_quantity=cargo_quantity,
    #     freight_rate=current_rate,
    #     distance_nm=distance_nm,
    #     vessel_speed=vessel["speed"] if "speed" in vessel else 14.2,
    #     fuel_price=fuel_price,
    #     fuel_consumption=fuel_consumption,
    #     port_cost=port_cost,
    #     waiting_days=1.2,
    #     demurrage_per_day=demurrage_per_day
    # )

    # print(f"Selected vessel: {vessel['vessel']}")
    # print(f"Freight cost: ${voyage['freight_cost']:,.2f}")
    # print(f"Fuel cost: ${voyage['fuel_cost']:,.2f}")
    # print(f"Port cost: ${voyage['port_cost']:,.2f}")
    # print(f"Waiting cost: ${voyage['waiting_cost']:,.2f}")
    # print(f"Total cost: ${voyage['total_cost']:,.2f}")
    # print(f"Cost/tonne: ${voyage['cost_per_tonne']:.2f}")

    ####
    print()
    print("3. VOYAGE ECONOMICS")
    print("-------------------")

    vessel_results = []

    for vessel in feasible:

        voyage = calculate_voyage_cost(
            cargo_quantity=cargo_quantity,
            freight_rate=current_rate,
            distance_nm=distance_nm,
            vessel_speed=float(vessel["speed"]),
            fuel_price=fuel_price,
            fuel_consumption=fuel_consumption,
            port_cost=port_cost,
            waiting_days=1.2,
            demurrage_per_day=demurrage_per_day
        )

        vessel_results.append({
            "vessel": vessel["vessel"],
            "total_cost": voyage["total_cost"],
            "cost_per_tonne": voyage["cost_per_tonne"],
            "fuel_cost": voyage["fuel_cost"],
            "voyage_days": voyage["voyage_days"]
        })

        print()
        print(vessel["vessel"])
        print(f"Voyage days: {voyage['voyage_days']}")
        print(f"Fuel cost: ${voyage['fuel_cost']:,.2f}")
        print(f"Total cost: ${voyage['total_cost']:,.2f}")
        print(f"Cost/tonne: ${voyage['cost_per_tonne']:.2f}")

    best_vessel = min(
        vessel_results,
        key=lambda x: x["total_cost"]
    )

    print()
    print("BEST VESSEL")
    print("-----------")
    print(best_vessel["vessel"])
    print(f"Total cost: ${best_vessel['total_cost']:,.2f}")
    ####

    print()
    print("4. RISK ANALYSIS")
    print("----------------")

    risk = simulate_freight_risk(
        current_rate=current_rate,
        forecast_rate=forecast_14,
        volatility=0.6,
        cargo_quantity=cargo_quantity,
        simulations=1000
    )

    print(f"P10: ${risk['p10_rate']:.2f}/tonne")
    print(f"P50: ${risk['p50_rate']:.2f}/tonne")
    print(f"P90: ${risk['p90_rate']:.2f}/tonne")

    print(
        f"Probability waiting is cheaper: "
        f"{risk['probability_wait_cheaper']:.2f}%"
    )

    print()
    print("5. FINAL RECOMMENDATION")
    print("-----------------------")

    if risk["probability_wait_cheaper"] >= 60:
        recommendation = "WAIT 14 DAYS"
    else:
        recommendation = "CHARTER NOW"

    print(f"Recommendation: {recommendation}")

    print()
    print("========================================")


if __name__ == "__main__":
    run_decision_engine()