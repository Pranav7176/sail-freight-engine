import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from decision_engine import run_decision
from economics.contract_strategy import evaluate_contract_strategy
from vessel_engine import find_feasible_vessels
from forecasting.xgboost_forecast import forecast_future
from economics.voyage_cost import calculate_voyage_cost
from economics.optimization import risk_adjusted_timing
from risk_engine import simulate_freight_risk
from scenario_engine import build_scenarios


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
    origin: str = "Australia",
    destination: str = "Dhamra"
):
    return run_decision(
        cargo_quantity=cargo_quantity,
        origin=origin,
        destination=destination
    )


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