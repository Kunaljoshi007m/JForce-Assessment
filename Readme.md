# Marketplace Delivery SLA Analysis — May 2026

Analyzes courier-level on-time delivery performance for a marketplace's May 2026 orders, comparing actual transit time against each order's promised SLA (service-level agreement) window.

## What the code does

1. Loads raw order data from a CSV file.
2. Cleans and standardizes courier names (trims whitespace, title-cases).
3. Parses all date/timestamp columns.
4. Filters the dataset down to **eligible orders**: delivered in May 2026, not flagged as test orders, and with complete `shipped_at`, `delivered_at`, and `promised_days` values.
5. Computes actual transit time (in days) and classifies each order as **On Time** or **Late** against its promised SLA.
6. Aggregates results by courier: order counts and on-time rate.
7. Prints a courier-level summary and the full row-level detail.
8. Generates two charts:
   - On-time delivery rate by courier (%)
   - Eligible vs. on-time order counts by courier
9. Exports the courier summary to `courier_delivery_performance_may_2026.csv`.

## Requirements

```bash
pip install pandas matplotlib seaborn
```

Tested with Python 3.9+.

## Input file

Place the raw CSV in the same directory as the script (or update `file_path`):

```
task1_marketplace_delivery_sla_raw.csv
```

Expected columns:

| Column           | Type      | Description                                  |
|-------------------|-----------|-----------------------------------------------|
| `order_id`        | string/int | Unique order identifier                      |
| `courier`         | string    | Courier/carrier name                          |
| `order_date`       | date      | Date the order was placed                     |
| `shipped_at`       | datetime  | Timestamp the order shipped                   |
| `delivered_at`     | datetime  | Timestamp the order was delivered             |
| `updated_at`       | datetime  | Last update timestamp                         |
| `promised_days`    | number    | SLA — promised delivery time in days          |
| `is_test_order`    | bool      | Flags internal/test orders to exclude         |

## Usage

Run the notebook/script cells top to bottom. It will:

- Print the courier summary table and eligible order detail to the console.
- Display two charts inline.
- Write `courier_delivery_performance_may_2026.csv` to the working directory.

## Output

**`courier_delivery_performance_may_2026.csv`** — one row per courier:

| Column           | Description                                 |
|-------------------|----------------------------------------------|
| `courier`         | Courier name                                 |
| `eligible_orders`  | Count of eligible May 2026 orders             |
| `on_time_orders`   | Count of those delivered within SLA           |
| `on_time_rate`     | `on_time_orders / eligible_orders`            |

## Methodology notes

- **Eligibility window**: an order is included if `delivered_at` falls between `2026-05-01` (inclusive) and `2026-06-01` (exclusive).
- **Transit time**: computed as `delivered_at - shipped_at`, in fractional days (not calendar days), then compared directly against `promised_days`.
- **Test orders**: excluded via `is_test_order != True`. Rows with a missing/`NaN` `is_test_order` value are **kept**, since `NaN != True` evaluates to `True` — confirm this matches the intended handling of unflagged orders.

## Known limitations

- Small sample sizes per courier can make the on-time rate misleading — a single order determines a 0% or 100% rate. Always check `eligible_orders` alongside `on_time_rate` before drawing conclusions.
- `actual_transit_days` is a continuous value compared against a (presumably) whole-number `promised_days`, implying the SLA is measured in exact 24-hour periods from shipment, not "by end of day N." Confirm this matches the actual SLA definition before treating results as final.
