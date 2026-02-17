## Example Output

```text
=== KPI REPORT ===
estimated_delivery_date  orders  boxes  delay_orders  delay_rate  mis_orders  mis_rate  r1_to_2  r1_to_3  round_change_orders  round_change_rate
             2026-02-16       4     10             2        50.0           1      25.0        1        1                    2               50.0
             2026-02-17       4      8             2        50.0           1      25.0        1        0                    1               25.0
==================
# Logistics KPI Mini Dashboard (CLI)

A simple Python CLI tool that aggregates delivery KPIs from a CSV file and prints a report.
It also exports a basic delay-rate chart for quick trend checks.

## Features
- KPI aggregation:
  - Delay rate (delayed orders / total orders)
  - Misdelivery rate
  - Round change rate (org round=1 → completion round=2 or 3)
- Group-by support:
  - `estimated_delivery_date`, `center_code`, `region_group_code`, etc.
- Export:
  - Saves a delay-rate chart to `out/`

## Quickstart (Mac)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python kpi_dashboard.py --csv data/sample_deliveries.csv
python kpi_dashboard.py --csv data/sample_deliveries.csv --group-by center_code
```
