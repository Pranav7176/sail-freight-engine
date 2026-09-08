def calculate_voyage_cost(
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

    freight_cost = cargo_quantity * freight_rate

    voyage_days = distance_nm / (vessel_speed * 24)

    fuel_used = voyage_days * fuel_consumption

    fuel_cost = fuel_used * fuel_price

    waiting_cost = waiting_days * demurrage_per_day

    total_cost = (
        freight_cost
        + fuel_cost
        + port_cost
        + waiting_cost
    )

    cost_per_tonne = total_cost / cargo_quantity

    return {
        "freight_cost": round(freight_cost, 2),
        "voyage_days": round(voyage_days, 2),
        "fuel_used": round(fuel_used, 2),
        "fuel_cost": round(fuel_cost, 2),
        "port_cost": round(port_cost, 2),
        "waiting_cost": round(waiting_cost, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_tonne": round(cost_per_tonne, 2)
    }


if __name__ == "__main__":

    result = calculate_voyage_cost(
        cargo_quantity=50000,
        freight_rate=19.00,
        distance_nm=3000,
        vessel_speed=14.2,
        fuel_price=600,
        fuel_consumption=35,
        port_cost=75000,
        waiting_days=1.2,
        demurrage_per_day=25000
    )

    print()
    print("VOYAGE ECONOMICS")
    print("================")

    for key, value in result.items():
        print(f"{key}: {value}")