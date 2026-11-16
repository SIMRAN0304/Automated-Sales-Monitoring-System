
import pandas as pd

# Load sales data
df = pd.read_csv("sales_data.csv")

# Calculate revenue for each order
df["revenue"] = df["quantity"] * df["unit_price"]

# Calculate total sales for each day
daily_sales = df.groupby("date")["revenue"].sum()

# Set sales threshold
threshold = 500

print("\nDAILY SALES REPORT")
print("------------------")

for date, sales in daily_sales.items():

    if sales < threshold:
        status = "LOW SALES ALERT"
    else:
        status = "NORMAL"

    print(f"{date}: €{sales:.2f} - {status}")
