from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vessel_engine import find_feasible_vessels
from forecasting.xgboost_forecast import forecast_future
from economics.voyage_cost import calculate_voyage_cost
from economics.optimization import risk_adjusted_timing
from risk_engine import simulate_freight_risk
from scenario_engine import run_scenario


app = FastAPI(
    title="SAIL Freight Decision Intelligence Engine",
    description="Decision support API for vessel chartering and bulk cargo procurement",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {
        "message": "SAIL Freight Decision Engine API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/forecast")
def get_forecast(
    vessel_class: str = "Panamax",
    days: int = 30
):
    forecast = forecast_future(
        vessel_class=vessel_class,
        days=days
    )

    return {
        "vessel_class": vessel_class,
        "days": days,
        "forecast": forecast
    }


@app.get("/api/decision")
def get_decision(
    cargo_quantity: int = 50000,
    destination: str = "Dhamra",
    vessel_class: str = "Panamax",
    current_rate: float = 19.00
):

    distance_nm = 3000
    fuel_price = 600
    fuel_consumption = 35
    port_cost = 75000
    waiting_days = 1.2
    demurrage_per_day = 25000

    vessels = find_feasible_vessels(
        cargo_quantity=cargo_quantity,
        destination=destination
    )

    if isinstance(vessels, dict):
        return vessels

    feasible = [
        vessel for vessel in vessels
        if vessel["status"] == "FEASIBLE"
        and vessel["class"] == vessel_class
    ]

    if not feasible:
        return {
            "error": "No feasible vessels found"
        }

    forecast = forecast_future(
        vessel_class=vessel_class,
        days=30
    )

    forecast_7 = forecast[6]["forecast"]
    forecast_14 = forecast[13]["forecast"]
    forecast_30 = forecast[29]["forecast"]

    vessel_results = []

    for vessel in feasible:

        economics = calculate_voyage_cost(
            cargo_quantity=cargo_quantity,
            freight_rate=current_rate,
            distance_nm=distance_nm,
            vessel_speed=vessel["speed"],
            fuel_price=fuel_price,
            fuel_consumption=fuel_consumption,
            port_cost=port_cost,
            waiting_days=waiting_days,
            demurrage_per_day=demurrage_per_day
        )

        vessel_results.append({
            "vessel": vessel["vessel"],
            "class": vessel["class"],
            "dwt": vessel["dwt"],
            "speed": vessel["speed"],
            "total_cost": economics["total_cost"],
            "cost_per_tonne": economics["cost_per_tonne"],
            "voyage_days": economics["voyage_days"],
            "fuel_cost": economics["fuel_cost"]
        })

    best_vessel = min(
        vessel_results,
        key=lambda x: x["total_cost"]
    )

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

    timing = risk_adjusted_timing(
        cargo_quantity=cargo_quantity,
        current_rate=current_rate,
        forecast_7=forecast_7,
        forecast_14=forecast_14,
        base_cost=best_vessel["total_cost"],
        risk_7=risk_7,
        risk_14=risk_14
    )

    if timing["recommendation"] == "CHARTER NOW":
        explanation = (
            "Current chartering has the lowest risk-adjusted cost. "
            "Potential savings from waiting are not sufficient "
            "to compensate for freight uncertainty."
        )
    elif timing["recommendation"] == "WAIT 7 DAYS":
        explanation = (
            "Waiting 7 days provides a better risk-adjusted cost "
            "than chartering immediately."
        )
    else:
        explanation = (
            "Waiting 14 days provides the lowest risk-adjusted cost "
            "under the current forecast and risk assumptions."
        )

    return {
        "cargo": {
            "quantity": cargo_quantity,
            "destination": destination,
            "vessel_class": vessel_class
        },

        "forecast": {
            "current": current_rate,
            "day_7": forecast_7,
            "day_14": forecast_14,
            "day_30": forecast_30
        },

        "vessels": vessel_results,

        "best_vessel": best_vessel,

        "risk": {
            "7_day": risk_7_analysis,
            "14_day": risk_14_analysis
        },

        "timing": timing,

        "recommendation": timing["recommendation"],

        "explanation": explanation
    }


@app.get("/api/scenario")
def get_scenario(
    cargo_quantity: int = 50000,
    freight_rate: float = 19.00,
    distance_nm: float = 3000,
    vessel_speed: float = 14.5,
    fuel_price: float = 600,
    fuel_consumption: float = 35,
    port_cost: float = 75000,
    waiting_days: float = 1.2,
    demurrage_per_day: float = 25000
):

    result = run_scenario(
        cargo_quantity=cargo_quantity,
        freight_rate=freight_rate,
        distance_nm=distance_nm,
        vessel_speed=vessel_speed,
        fuel_price=fuel_price,
        fuel_consumption=fuel_consumption,
        port_cost=port_cost,
        waiting_days=waiting_days,
        demurrage_per_day=demurrage_per_day
    )

    return {
        "inputs": {
            "cargo_quantity": cargo_quantity,
            "freight_rate": freight_rate,
            "distance_nm": distance_nm,
            "vessel_speed": vessel_speed,
            "fuel_price": fuel_price,
            "fuel_consumption": fuel_consumption,
            "port_cost": port_cost,
            "waiting_days": waiting_days,
            "demurrage_per_day": demurrage_per_day
        },
        "result": result
    }