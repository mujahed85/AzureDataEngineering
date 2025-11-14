import pandas as pd

# Load bronze data
df = pd.read_csv("./bronze_files/customers_bronze.csv")

print("\n--- BRONZE DATA ---")
print(df)

# 1. Remove missing names
df = df.dropna(subset=["name"])

# 2. Convert name to Proper Case
df["name"] = df["name"].str.title()

# 3. Remove rows where salary < 50000 (example cleaning rule)
df = df[df["salary"] >= 50000]

# 4. Remove duplicates
df = df.drop_duplicates()

# Save as Silver CSV and Parquet
df.to_csv("./silver_files/customers_silver.csv", index=False)
df.to_parquet("./silver_files/customers_silver.parquet", engine="pyarrow")

print("\n--- SILVER DATA (Cleaned) ---")
print(df)