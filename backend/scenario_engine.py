from economics.voyage_cost import calculate_voyage_cost


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
    probability_14
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
        }
    }