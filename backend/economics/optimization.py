def risk_adjusted_timing(
    cargo_quantity,
    current_rate,
    forecast_7,
    forecast_14,
    base_cost,
    risk_7,
    risk_14,
    probability_7=None,
    probability_14=None
):

    now_cost = base_cost

    wait_7_cost = base_cost + (
        (forecast_7 - current_rate) * cargo_quantity
    )

    wait_14_cost = base_cost + (
        (forecast_14 - current_rate) * cargo_quantity
    )

    saving_7 = now_cost - wait_7_cost
    saving_14 = now_cost - wait_14_cost

    risk_penalty_7 = risk_7 * now_cost
    risk_penalty_14 = risk_14 * now_cost

    adjusted_7 = wait_7_cost + risk_penalty_7
    adjusted_14 = wait_14_cost + risk_penalty_14

    if probability_7 is None:
        probability_7 = 50.0

    if probability_14 is None:
        probability_14 = 50.0

    options = {
        "CHARTER NOW": now_cost,
        "WAIT 7 DAYS": adjusted_7,
        "WAIT 14 DAYS": adjusted_14
    }

    best_option = min(options, key=options.get)

    if (
        best_option == "WAIT 7 DAYS"
        and probability_7 < 55
    ):
        best_option = "CHARTER NOW"

    if (
        best_option == "WAIT 14 DAYS"
        and probability_14 < 55
    ):
        best_option = "CHARTER NOW"

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

        "probability_wait_cheaper_7": round(
            probability_7, 2
        ),

        "probability_wait_cheaper_14": round(
            probability_14, 2
        ),

        "recommendation": best_option
    }