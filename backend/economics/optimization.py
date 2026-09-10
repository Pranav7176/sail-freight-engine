def risk_adjusted_timing(
    cargo_quantity,
    current_rate,
    forecast_7,
    forecast_14,
    base_cost,
    risk_7,
    risk_14
):
    now_cost = base_cost

    wait_7_cost = base_cost + ((forecast_7 - current_rate) * cargo_quantity)

    wait_14_cost = base_cost + ((forecast_14 - current_rate) * cargo_quantity)

    saving_7 = now_cost - wait_7_cost
    saving_14 = now_cost - wait_14_cost

    risk_penalty_7 = now_cost * risk_7
    risk_penalty_14 = now_cost * risk_14

    adjusted_7 = wait_7_cost + risk_penalty_7
    adjusted_14 = wait_14_cost + risk_penalty_14

    adjusted_options = {
        "CHARTER NOW": now_cost,
        "WAIT 7 DAYS": adjusted_7,
        "WAIT 14 DAYS": adjusted_14
    }

    best_option = min(adjusted_options, key=adjusted_options.get)

    return {
        "now_cost": round(now_cost, 2),

        "wait_7_cost": round(wait_7_cost, 2),
        "wait_14_cost": round(wait_14_cost, 2),

        "saving_7": round(saving_7, 2),
        "saving_14": round(saving_14, 2),

        "risk_penalty_7": round(risk_penalty_7, 2),
        "risk_penalty_14": round(risk_penalty_14, 2),

        "adjusted_7": round(adjusted_7, 2),
        "adjusted_14": round(adjusted_14, 2),

        "recommendation": best_option
    }