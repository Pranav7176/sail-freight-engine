import pandas as pd


def find_feasible_vessels(cargo_quantity, destination):
    vessels = pd.read_csv("data/vessels.csv")
    ports = pd.read_csv("data/ports.csv")

    port = ports[ports["port"] == destination]

    if port.empty:
        return {"error": f"Port '{destination}' not found"}

    port = port.iloc[0]

    results = []

    for _, vessel in vessels.iterrows():

        reasons = []

        if vessel["availability"] != "Available":
            reasons.append("Vessel is currently unavailable")

        if vessel["dwt"] < cargo_quantity:
            reasons.append("Vessel DWT is insufficient")

        if vessel["draft"] > port["max_draft"]:
            reasons.append("Vessel draft exceeds port limit")

        if vessel["loa"] > port["max_loa"]:
            reasons.append("Vessel LOA exceeds port limit")

        if vessel["beam"] > port["max_beam"]:
            reasons.append("Vessel beam exceeds port limit")

        if reasons:
            status = "NOT FEASIBLE"
        else:
            status = "FEASIBLE"

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


if __name__ == "__main__":
    results = find_feasible_vessels(
        cargo_quantity=75000,
        destination="Dhamra"
    )

    for vessel in results:
        print(vessel)