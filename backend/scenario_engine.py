from economics.voyage_cost import calculate_voyage_cost
from economics.optimization import risk_adjusted_timing


def build_scenarios(
    cargo_quantity,
    current_rate,
    forecast_7,
    forecast_14,
    distance_nm,
    vessel_speed,
    fuel_price,
    fuel_consumption,
    port_cost,
    waiting_days,
    demurrage_per_day,
    probability_7,
    probability_14,
    risk_7=0,
    risk_14=0
):

    now_voyage = calculate_voyage_cost(
        cargo_quantity=cargo_quantity,
        freight_rate=current_rate,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days,
        demurrage_per_day=demurrage_per_day
    )

    wait_7_voyage = calculate_voyage_cost(
        cargo_quantity=cargo_quantity,
        freight_rate=forecast_7,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days,
        demurrage_per_day=demurrage_per_day
    )

    wait_14_voyage = calculate_voyage_cost(
        cargo_quantity=cargo_quantity,
        freight_rate=forecast_14,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days,
        demurrage_per_day=demurrage_per_day
    )

    now_cost = now_voyage["total_cost"]
    wait_7_cost = wait_7_voyage["total_cost"]
    wait_14_cost = wait_14_voyage["total_cost"]

    saving_7 = now_cost - wait_7_cost
    saving_14 = now_cost - wait_14_cost

    def stress_result(label, voyage):
        total_cost = voyage["total_cost"]
        impact = total_cost - now_cost
        impact_percent = (
            (impact / now_cost) * 100
            if now_cost != 0
            else 0
        )

        return {
            "label": label,
            "total_cost": float(round(total_cost, 2)),
            "cost_per_tonne": float(
                round(voyage["cost_per_tonne"], 2)
            ),
            "cost_impact": float(round(impact, 2)),
            "cost_impact_percent": float(
                round(impact_percent, 2)
            )
        }

    freight_stress = calculate_voyage_cost(
        cargo_quantity=cargo_quantity,
        freight_rate=current_rate * 1.10,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days,
        demurrage_per_day=demurrage_per_day
    )

    fuel_stress = calculate_voyage_cost(
        cargo_quantity=cargo_quantity,
        freight_rate=current_rate,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price * 1.15,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days,
        demurrage_per_day=demurrage_per_day
    )

    congestion_stress = calculate_voyage_cost(
        cargo_quantity=cargo_quantity,
        freight_rate=current_rate,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days + 2,
        demurrage_per_day=demurrage_per_day
    )

    combined_stress = calculate_voyage_cost(
        cargo_quantity=cargo_quantity,
        freight_rate=current_rate * 1.10,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price * 1.15,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days + 2,
        demurrage_per_day=demurrage_per_day
    )

    base_timing = risk_adjusted_timing(
        cargo_quantity=cargo_quantity,
        current_rate=current_rate,
        forecast_7=forecast_7,
        forecast_14=forecast_14,
        base_cost=now_cost,
        risk_7=risk_7,
        risk_14=risk_14,
        probability_7=probability_7,
        probability_14=probability_14
    )

    stress_timings = {}

    stress_cases = {
        "freight_plus_10": {
            "current_rate": current_rate,
            "forecast_7": forecast_7 * 1.10,
            "forecast_14": forecast_14 * 1.10,
            "base_cost": now_cost
        },

        "fuel_plus_15": {
            "current_rate": current_rate,
            "forecast_7": forecast_7,
            "forecast_14": forecast_14,
            "base_cost": fuel_stress["total_cost"]
        },

        "congestion_plus_2": {
            "current_rate": current_rate,
            "forecast_7": forecast_7,
            "forecast_14": forecast_14,
            "base_cost": congestion_stress["total_cost"]
        },

        "combined": {
            "current_rate": current_rate,
            "forecast_7": forecast_7 * 1.10,
            "forecast_14": forecast_14 * 1.10,
            "base_cost": combined_stress["total_cost"]
        }
    }

    for scenario_name, values in stress_cases.items():

        timing_result = risk_adjusted_timing(
            cargo_quantity=cargo_quantity,
            current_rate=values["current_rate"],
            forecast_7=values["forecast_7"],
            forecast_14=values["forecast_14"],
            base_cost=values["base_cost"],
            risk_7=risk_7,
            risk_14=risk_14,
            probability_7=probability_7,
            probability_14=probability_14
        )

        stress_timings[scenario_name] = {
            "base_decision": base_timing["recommendation"],
            "stress_decision": timing_result["recommendation"],
            "decision_changed": (
                timing_result["recommendation"]
                != base_timing["recommendation"]
            )
        }

    return {
        "current": {
            "label": "CHARTER NOW",
            "freight_rate": float(round(current_rate, 2)),
            "total_cost": float(round(now_cost, 2)),
            "cost_per_tonne": float(
                round(now_voyage["cost_per_tonne"], 2)
            )
        },

        "wait_7": {
            "label": "WAIT 7 DAYS",
            "forecast_rate": float(round(forecast_7, 2)),
            "total_cost": float(round(wait_7_cost, 2)),
            "cost_per_tonne": float(
                round(wait_7_voyage["cost_per_tonne"], 2)
            ),
            "estimated_saving": float(round(saving_7, 2)),
            "probability_wait_cheaper": float(
                round(float(probability_7), 2)
            )
        },

        "wait_14": {
            "label": "WAIT 14 DAYS",
            "forecast_rate": float(round(forecast_14, 2)),
            "total_cost": float(round(wait_14_cost, 2)),
            "cost_per_tonne": float(
                round(wait_14_voyage["cost_per_tonne"], 2)
            ),
            "estimated_saving": float(round(saving_14, 2)),
            "probability_wait_cheaper": float(
                round(float(probability_14), 2)
            )
        },

                "stress_analysis": {
            "base": {
                "label": "BASE CASE",
                "total_cost": float(round(now_cost, 2)),
                "cost_per_tonne": float(
                    round(now_voyage["cost_per_tonne"], 2)
                )
            },

            "freight_plus_10": stress_result(
                "FREIGHT +10%",
                freight_stress
            ),

            "fuel_plus_15": stress_result(
                "FUEL +15%",
                fuel_stress
            ),

            "congestion_plus_2": stress_result(
                "CONGESTION +2 DAYS",
                congestion_stress
            ),

            "combined": stress_result(
                "COMBINED MARKET STRESS",
                combined_stress
            ),

            "resilience": {
                "base_decision": base_timing["recommendation"],
                "scenarios": stress_timings
            }
        }
    }