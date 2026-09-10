import pandas as pd

from economics.optimization import risk_adjusted_timing
from vessel_engine import find_feasible_vessels
from economics.voyage_cost import calculate_voyage_cost
from forecasting.xgboost_forecast import forecast_future
from risk_engine import simulate_freight_risk
from economics.optimization import risk_adjusted_timing


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

    risk_7_analysis = simulate_freight_risk(
        current_rate=current_rate,
        forecast_rate=forecast_7,
        cargo_quantity=cargo_quantity,
        simulations=1000
    )

    risk_14_analysis = simulate_freight_risk(
        current_rate=current_rate,
        forecast_rate=forecast_14,
        cargo_quantity=cargo_quantity,
        simulations=1000
    )

    risk_7 = (
        risk_7_analysis["expected_downside_cost"]
        / best_vessel["total_cost"]
    )

    risk_14 = (
        risk_14_analysis["expected_downside_cost"]
        / best_vessel["total_cost"]
    )
    

    print("7-DAY SCENARIO")
    print(f"P10: ${risk_7_analysis['p10_rate']:.2f}/tonne")
    print(f"P50: ${risk_7_analysis['p50_rate']:.2f}/tonne")
    print(f"P90: ${risk_7_analysis['p90_rate']:.2f}/tonne")
    print(
        f"Probability waiting is cheaper: "
        f"{risk_7_analysis['probability_wait_cheaper']:.2f}%"
    )
    print(
        f"Expected downside: "
        f"${risk_7_analysis['expected_downside_cost']:,.2f}"
    )

    print()
    print("14-DAY SCENARIO")
    print(f"P10: ${risk_14_analysis['p10_rate']:.2f}/tonne")
    print(f"P50: ${risk_14_analysis['p50_rate']:.2f}/tonne")
    print(f"P90: ${risk_14_analysis['p90_rate']:.2f}/tonne")
    print(
        f"Probability waiting is cheaper: "
        f"{risk_14_analysis['probability_wait_cheaper']:.2f}%"
    )
    print(
        f"Expected downside: "
        f"${risk_14_analysis['expected_downside_cost']:,.2f}"
    )

    timing = risk_adjusted_timing(
            cargo_quantity=cargo_quantity,
            current_rate=current_rate,
            forecast_7=forecast_7,
            forecast_14=forecast_14,
            base_cost=best_vessel["total_cost"],
            risk_7=risk_7,
            risk_14=risk_14
        )

    print()
    print("5. RISK-ADJUSTED CHARTER TIMING")
    print("-------------------------------")

    print(f"CHARTER NOW: ${timing['now_cost']:,.2f}")

    print()
    print(f"WAIT 7 DAYS")
    print(f"Expected Cost: ${timing['wait_7_cost']:,.2f}")
    print(f"Expected Saving: ${timing['saving_7']:,.2f}")
    print(f"Risk Penalty: ${timing['risk_penalty_7']:,.2f}")
    print(f"Risk-Adjusted Cost: ${timing['adjusted_7']:,.2f}")

    print()
    print(f"WAIT 14 DAYS")
    print(f"Expected Cost: ${timing['wait_14_cost']:,.2f}")
    print(f"Expected Saving: ${timing['saving_14']:,.2f}")
    print(f"Risk Penalty: ${timing['risk_penalty_14']:,.2f}")
    print(f"Risk-Adjusted Cost: ${timing['adjusted_14']:,.2f}")

    print()
    print("6. FINAL RECOMMENDATION")
    print("-----------------------")
    print(f"Recommendation: {timing['recommendation']}")
    print()
    print("========================================")


if __name__ == "__main__":
    run_decision_engine()