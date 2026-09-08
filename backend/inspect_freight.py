import pandas as pd

df = pd.read_csv("data/freight.csv")

print("Shape:")
print(df.shape)

print("\nVessel classes:")
print(df["vessel_class"].unique())

print("\nAverage freight by vessel class:")
print(df.groupby("vessel_class")["freight_rate"].mean())

print("\nMinimum / Maximum:")
print(df.groupby("vessel_class")["freight_rate"].agg(["min", "max"]))