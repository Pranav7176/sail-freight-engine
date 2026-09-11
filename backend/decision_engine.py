import pandas as pd
import numpy as np

from scenario_engine import build_scenarios
from market_data import get_current_rate
from vessel_engine import find_feasible_vessels
from forecasting.xgboost_forecast import forecast_future
from economics.voyage_cost import calculate_voyage_cost
from economics.optimization import risk_adjusted_timing
from risk_engine import simulate_freight_risk
from economics.contract_strategy import evaluate_contract_strategy


def get_route_data(origin, destination):
    routes = pd.read_csv("data/routes.csv")
    ports = pd.read_csv("data/ports.csv")

    route = routes[
        (routes["origin"] == origin) &
        (routes["destination"] == destination)
    ]

    port = ports[ports["port"] == destination]

    if route.empty:
        return None, None

    if port.empty:
        return None, None

    return route.iloc[0], port.iloc[0]


def run_decision(cargo_quantity, origin, destination):

    route, port = get_route_data(origin, destination)

    if route is None:
        return {
            "error": f"No route data available for {origin} → {destination}"
        }

    feasible_vessels = find_feasible_vessels(
        cargo_quantity,
        origin,
        destination
    )

    if isinstance(feasible_vessels, dict):
        return feasible_vessels

    vessel_analysis = []
    rejected_vessels = []

    for vessel in feasible_vessels:

        if vessel["status"] != "FEASIBLE":

            rejected_vessels.append({
                "vessel": vessel["vessel"],
                "class": vessel["class"],
                "dwt": vessel["dwt"],
                "status": "NOT FEASIBLE",
                "reasons": vessel.get(
                    "reasons",
                    ["Vessel does not satisfy route constraints"]
                )
            })

            continue

        current_rate = get_current_rate(
            origin,
            destination,
            vessel["class"]
        )

        if current_rate is None:
            rejected_vessels.append({
                "vessel": vessel["vessel"],
                "class": vessel["class"],
                "dwt": vessel["dwt"],
                "status": "NOT FEASIBLE",
                "reasons": [
                    "No freight rate available for this vessel class and route"
                ]
            })
            continue

        try:
            forecast = forecast_future(
                origin,
                destination,
                vessel["class"]
            )

            if len(forecast) < 14:
                raise ValueError("Insufficient forecast horizon")

            average_forecast = float(
                np.mean([
                    item["forecast"]
                    for item in forecast
                ])
            )

        except Exception:
            rejected_vessels.append({
                "vessel": vessel["vessel"],
                "class": vessel["class"],
                "dwt": vessel["dwt"],
                "status": "NOT FEASIBLE",
                "reasons": [
                    "Freight forecast unavailable for this vessel class"
                ]
            })
            continue

        voyage = calculate_voyage_cost(
            cargo_quantity=cargo_quantity,
            freight_rate=current_rate,
            distance_nm=float(route["distance_nm"]),
            vessel_speed=vessel["speed"],
            fuel_price=600,
            fuel_consumption=35,
            port_cost=float(port["handling_rate"]),
            waiting_days=float(port["waiting_days"]),
            demurrage_per_day=25000
        )

        risk = simulate_freight_risk(
            current_rate=current_rate,
            forecast_rate=forecast[6]["forecast"],
            cargo_quantity=cargo_quantity
        )

        risk_cost = risk["expected_downside_cost"]

        risk_adjusted_cost = (
            voyage["total_cost"] + risk_cost
        )

        vessel_analysis.append({
            "vessel": vessel["vessel"],
            "class": vessel["class"],
            "dwt": vessel["dwt"],
            "loa": vessel["loa"],
            "beam": vessel["beam"],
            "draft": vessel["draft"],
            "speed": vessel["speed"],
            "status": "FEASIBLE",

            "total_cost": round(
                voyage["total_cost"],
                2
            ),

            "cost_per_tonne": round(
                voyage["cost_per_tonne"],
                2
            ),

            "voyage_days": round(
                voyage["voyage_days"],
                2
            ),

            "fuel_cost": round(
                voyage["fuel_cost"],
                2
            ),

            "freight_cost": round(
                voyage["freight_cost"],
                2
            ),

            "waiting_cost": round(
                voyage["waiting_cost"],
                2
            ),

            "forecast_average": round(
                average_forecast,
                2
            ),

            "current_rate": round(
                current_rate,
                2
            ),

            "forecast_7_day": round(
                forecast[6]["forecast"],
                2
            ),

            "risk_cost": round(
                risk_cost,
                2
            ),

            "risk_adjusted_cost": round(
                risk_adjusted_cost,
                2
            ),

            "risk_adjusted_cost_per_tonne": round(
                risk_adjusted_cost / cargo_quantity,
                2
            )
        })

    if not vessel_analysis:
        return {
            "error": "No feasible vessel available for this cargo and destination.",
            "rejected_vessels": rejected_vessels
        }

    # ---------------------------------------------------------
    # SELECT VESSEL USING RISK-ADJUSTED TOTAL COST
    # ---------------------------------------------------------

    best_vessel = min(
        vessel_analysis,
        key=lambda x: x["risk_adjusted_cost"]
    )

    for vessel in vessel_analysis:
        if vessel["vessel"] == best_vessel["vessel"]:
            vessel["selection_status"] = "SELECTED"
        else:
            vessel["selection_status"] = "FEASIBLE"

    selected_class = best_vessel["class"]

    current_rate = best_vessel["current_rate"]

    # ---------------------------------------------------------
    # FULL FREIGHT FORECAST
    # ---------------------------------------------------------

    try:
        full_forecast = forecast_future(
            origin,
            destination,
            selected_class
        )

    except Exception:
        full_forecast = []

    if len(full_forecast) < 30:
        return {
            "error": (
                f"No complete 30-day freight forecast available "
                f"for vessel class {selected_class}"
            )
        }

    forecast_values = [
        item["forecast"]
        for item in full_forecast
    ]

    day_7 = forecast_values[6]
    day_14 = forecast_values[13]
    day_30 = forecast_values[29]

    # ---------------------------------------------------------
    # RISK ANALYSIS
    # ---------------------------------------------------------

    risk = simulate_freight_risk(
        current_rate=current_rate,
        forecast_rate=day_7,
        cargo_quantity=cargo_quantity
    )

    risk_7 = (
        risk["expected_downside_cost"]
        / best_vessel["total_cost"]
    )

    risk_14_result = simulate_freight_risk(
        current_rate=current_rate,
        forecast_rate=day_14,
        cargo_quantity=cargo_quantity
    )

    risk_14 = (
        risk_14_result["expected_downside_cost"]
        / best_vessel["total_cost"]
    )

    # ---------------------------------------------------------
    # CHARTER TIMING
    # ---------------------------------------------------------

    timing = risk_adjusted_timing(
        cargo_quantity=cargo_quantity,
        current_rate=current_rate,
        forecast_7=day_7,
        forecast_14=day_14,
        base_cost=best_vessel["total_cost"],
        risk_7=risk_7,
        risk_14=risk_14,
        probability_7=risk["probability_wait_cheaper"],
        probability_14=risk_14_result[
            "probability_wait_cheaper"
        ]
    )

    # ---------------------------------------------------------
    # VOYAGE SCENARIOS
    # ---------------------------------------------------------

    scenarios = build_scenarios(
        cargo_quantity=cargo_quantity,
        current_rate=current_rate,
        forecast_7=day_7,
        forecast_14=day_14,
        distance_nm=float(route["distance_nm"]),
        vessel_speed=best_vessel["speed"],
        fuel_price=600,
        fuel_consumption=35,
        port_cost=float(port["handling_rate"]),
        waiting_days=float(port["waiting_days"]),
        demurrage_per_day=25000,
        probability_7=risk[
            "probability_wait_cheaper"
        ],
        probability_14=risk_14_result[
            "probability_wait_cheaper"
        ],
        risk_7=risk_7,
        risk_14=risk_14
    )

    # ---------------------------------------------------------
    # CONTRACT STRATEGY
    # ---------------------------------------------------------

    contract_strategy = evaluate_contract_strategy(
        cargo_quantity=cargo_quantity,
        current_rate=current_rate,
        forecast=full_forecast,
        volatility=np.std(forecast_values)
    )

    # ---------------------------------------------------------
    # FINAL RECOMMENDATION
    # ---------------------------------------------------------

    final_recommendation = (
        f"{contract_strategy['recommendation']} "
        f"{timing['recommendation']}"
    )

    # ---------------------------------------------------------
    # VESSEL SELECTION EXPLANATION
    # ---------------------------------------------------------

    vessel_selection_explanation = (
        f"{best_vessel['vessel']} ({best_vessel['class']}) "
        f"was selected because it has the lowest "
        f"risk-adjusted total voyage cost among all feasible "
        f"vessels for the {cargo_quantity:,}-tonne "
        f"{origin} → {destination} movement."
    )

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------

    return {

        "cargo": {
            "quantity": cargo_quantity,
            "origin": origin,
            "destination": destination
        },

        "route": {
            "distance_nm": float(
                route["distance_nm"]
            )
        },

        "port": {
            "name": destination,
            "max_draft": float(
                port["max_draft"]
            ),
            "max_loa": float(
                port["max_loa"]
            ),
            "max_beam": float(
                port["max_beam"]
            ),
            "handling_rate": float(
                port["handling_rate"]
            ),
            "congestion": float(
                port["congestion"]
            ),
            "waiting_days": float(
                port["waiting_days"]
            )
        },

        "forecast": {
            "vessel_class": selected_class,
            "current": current_rate,
            "day_7": day_7,
            "day_14": day_14,
            "day_30": day_30,
            "full": full_forecast
        },

        "vessel_analysis": vessel_analysis,

        "rejected_vessels": rejected_vessels,

        "best_vessel": best_vessel,

        "vessel_selection": {
            "selected_vessel": best_vessel["vessel"],
            "selected_class": best_vessel["class"],
            "selection_basis": [
                "Cargo capacity",
                "Loading-port constraints",
                "Destination-port constraints",
                "Vessel availability",
                "Voyage economics",
                "Freight risk",
                "Lowest risk-adjusted total cost"
            ],
            "explanation": vessel_selection_explanation
        },

        "risk": {
            "7_day": risk,
            "14_day": risk_14_result
        },

        "timing": timing,

        "contract_strategy": contract_strategy,

        "scenarios": scenarios,

        "recommendation": final_recommendation,

        "explanation": (
            f"{vessel_selection_explanation} "
            f"The freight risk engine recommends "
            f"{timing['recommendation'].lower()}, "
            f"while the contract strategy engine recommends "
            f"{contract_strategy['recommendation'].lower()}."
        )
    }