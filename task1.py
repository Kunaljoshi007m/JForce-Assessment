import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


file_path = "task1_marketplace_delivery_sla_raw.csv"

df = pd.read_csv(file_path)

if "courier" in df.columns:
    df["courier"] = df["courier"].astype(str).str.strip().str.title()

date_columns = [
    "order_date",
    "shipped_at",
    "delivered_at",
    "updated_at"
]

for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors="coerce")


may_2026 = (
    (df["delivered_at"] >= "2026-05-01") &
    (df["delivered_at"] < "2026-06-01")
)

eligible = df[
    may_2026 &
    (df["is_test_order"] != True) &
    df["shipped_at"].notna() &
    df["delivered_at"].notna() &
    df["promised_days"].notna()
].copy()


eligible["actual_transit_days"] = (
    eligible["delivered_at"] - eligible["shipped_at"]
).dt.total_seconds() / (24 * 60 * 60)


eligible["delivery_status"] = (
    eligible["actual_transit_days"]
    <= eligible["promised_days"]
).map({
    True: "On Time",
    False: "Late"
})


courier_summary = (
    eligible
    .groupby("courier")
    .agg(
        eligible_orders=("order_id", "count"),
        on_time_orders=("delivery_status", lambda x: (x == "On Time").sum())
    )
    .reset_index()
)

courier_summary["on_time_rate"] = (
    courier_summary["on_time_orders"] /
    courier_summary["eligible_orders"]
)

courier_summary = courier_summary.sort_values("courier").reset_index(drop=True)


print("\nCourier-Level Delivery Performance:")
print(courier_summary)


print("\nEligible May 2026 Orders:")
print(
    eligible[
        [
            "order_id",
            "courier",
            "shipped_at",
            "delivered_at",
            "promised_days",
            "actual_transit_days",
            "delivery_status"
        ]
    ]
)


sns.set_theme(style="whitegrid")

plt.figure(figsize=(10, 6))

ax = sns.barplot(
    data=courier_summary,
    x="courier",
    y="on_time_rate",
    color="steelblue"
)

plt.title("On-Time Delivery Rate by Courier - May 2026")
plt.xlabel("Courier")
plt.ylabel("On-Time Rate")


for container in ax.containers:
    ax.bar_label(
        container,
        labels=[f"{value.get_height():.1%}" for value in container],
        padding=3
    )

plt.ylim(0, 1.1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


plot_data = courier_summary.melt(
    id_vars="courier",
    value_vars=["eligible_orders", "on_time_orders"],
    var_name="metric",
    value_name="orders"
)

plot_data["metric"] = plot_data["metric"].replace({
    "eligible_orders": "Eligible Orders",
    "on_time_orders": "On-Time Orders"
})

plt.figure(figsize=(10, 6))

ax = sns.barplot(
    data=plot_data,
    x="courier",
    y="orders",
    hue="metric"
)

plt.title("Eligible vs. On-Time Orders by Courier - May 2026")
plt.xlabel("Courier")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)

for container in ax.containers:
    ax.bar_label(container, padding=2)

plt.tight_layout()
plt.show()

courier_summary.to_csv(
    "courier_delivery_performance_may_2026.csv",
    index=False
)