import pandas as pd

# Load silver layer
df = pd.read_parquet("./silver_files/customers_silver.parquet")

print("\n--- SILVER CLEANED DATA ---")
print(df)

# --- GOLD LEVEL AGGREGATION ---

# 1. Aggregation: Salary summary per city
gold_df = df.groupby("city").agg(
    avg_salary=("salary", "mean"),
    max_salary=("salary", "max"),
    customer_count=("id", "count")
).reset_index()

# Save gold output
gold_df.to_csv("./gold_files/customers_gold.csv", index=False)
gold_df.to_parquet("./gold_files/customers_gold.parquet", engine="pyarrow")

print("\n--- GOLD AGGREGATED DATA ---")
print(gold_df)