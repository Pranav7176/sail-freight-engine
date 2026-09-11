import pandas as pd


def check_vessel_constraints(vessel, port, location):
    reasons = []

    if vessel["draft"] > port["max_draft"]:
        reasons.append(
            f"{location} draft limit exceeded"
        )

    if vessel["loa"] > port["max_loa"]:
        reasons.append(
            f"{location} LOA limit exceeded"
        )

    if vessel["beam"] > port["max_beam"]:
        reasons.append(
            f"{location} beam limit exceeded"
        )

    return reasons


def find_feasible_vessels(cargo_quantity, origin, destination):

    vessels = pd.read_csv("data/vessels.csv")
    destination_ports = pd.read_csv("data/ports.csv")
    loading_ports = pd.read_csv("data/loading_ports.csv")

    destination_port = destination_ports[
        destination_ports["port"] == destination
    ]

    if destination_port.empty:
        return {
            "error": f"Destination port '{destination}' not found"
        }

    loading_port = loading_ports[
        loading_ports["origin"] == origin
    ]

    if loading_port.empty:
        return {
            "error": f"Loading region '{origin}' not found"
        }

    destination_port = destination_port.iloc[0]
    loading_port = loading_port.iloc[0]

    results = []

    for _, vessel in vessels.iterrows():

        reasons = []

        if vessel["availability"] != "Available":
            reasons.append(
                "Vessel is currently unavailable"
            )

        if vessel["dwt"] < cargo_quantity:
            reasons.append(
                "Vessel DWT is insufficient"
            )

        loading_reasons = check_vessel_constraints(
            vessel,
            loading_port,
            "Loading port"
        )

        destination_reasons = check_vessel_constraints(
            vessel,
            destination_port,
            "Destination port"
        )

        reasons.extend(loading_reasons)
        reasons.extend(destination_reasons)

        status = (
            "FEASIBLE"
            if not reasons
            else "NOT FEASIBLE"
        )

        results.append({
            "vessel": vessel["name"],
            "class": vessel["vessel_class"],
            "dwt": vessel["dwt"],
            "loa": vessel["loa"],
            "beam": vessel["beam"],
            "draft": vessel["draft"],
            "speed": vessel["speed"],
            "status": status,
            "reasons": reasons
        })

    return results