import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    df["pdt"] = pd.to_datetime(df["pdt"], errors="coerce")
    df["estimated_delivery_date"] = pd.to_datetime(df["estimated_delivery_date"], errors="coerce")

    int_cols = ["org_delivery_round", "delivery_completion_round", "is_delayed", "is_misdelivered", "box_cnt"]
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    df["_uniq_key"] = (
        df["estimated_delivery_date"].astype(str)
        + "|"
        + df["worker_id"].astype(str)
        + "|"
        + df["region_group_code"].astype(str)
        + "|"
        + df["delivery_completion_round"].astype(str)
        + "|"
        + df["full_address_hash"].astype(str)
    )
    return df


def summarize(df: pd.DataFrame, group_by: str | None) -> pd.DataFrame:
    groups = df.groupby(group_by, dropna=False) if group_by else [(None, df)]
    rows = []

    for k, part in groups:
        total_orders = part["_uniq_key"].nunique()
        total_boxes = int(part["box_cnt"].sum())

        delayed_orders = part.loc[part["is_delayed"] == 1, "_uniq_key"].nunique()
        mis_orders = part.loc[part["is_misdelivered"] == 1, "_uniq_key"].nunique()

        r1_to_2 = part.loc[(part["org_delivery_round"] == 1) & (part["delivery_completion_round"] == 2), "_uniq_key"].nunique()
        r1_to_3 = part.loc[(part["org_delivery_round"] == 1) & (part["delivery_completion_round"] == 3), "_uniq_key"].nunique()
        round_change = r1_to_2 + r1_to_3

        def rate(n: int, d: int) -> float:
            return (n / d) if d else 0.0

        rows.append(
            {
                group_by if group_by else "ALL": k if group_by else "ALL",
                "orders": total_orders,
                "boxes": total_boxes,
                "delay_orders": delayed_orders,
                "delay_rate": rate(delayed_orders, total_orders),
                "mis_orders": mis_orders,
                "mis_rate": rate(mis_orders, total_orders),
                "r1_to_2": r1_to_2,
                "r1_to_3": r1_to_3,
                "round_change_orders": round_change,
                "round_change_rate": rate(round_change, total_orders),
            }
        )

    return pd.DataFrame(rows)


def print_report(summary_df: pd.DataFrame) -> None:
    df = summary_df.copy()
    for c in ["delay_rate", "mis_rate", "round_change_rate"]:
        df[c] = (df[c] * 100).round(2)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 50)
    print("\n=== KPI REPORT ===")
    print(df.to_string(index=False))
    print("==================\n")


def save_delay_rate_chart(summary_df: pd.DataFrame, x_col: str, out_path: Path) -> None:
    if len(summary_df) <= 1:
        return

    df = summary_df.sort_values(by=x_col).copy()
    plt.figure()
    plt.plot(df[x_col].astype(str), df["delay_rate"])
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Logistics KPI mini dashboard (CLI)")
    parser.add_argument("--csv", required=True, help="Path to deliveries CSV")
    parser.add_argument(
        "--group-by",
        default="estimated_delivery_date",
        help="Group column (estimated_delivery_date, center_code, region_group_code, etc.)",
    )
    parser.add_argument("--out-dir", default="out", help="Output directory for charts")
    args = parser.parse_args()

    df = load_data(args.csv)

    group_by = args.group_by if args.group_by in df.columns else None
    if args.group_by and group_by is None:
        print(f"[WARN] group-by='{args.group_by}' not found. Using overall summary.")

    summary_df = summarize(df, group_by)
    print_report(summary_df)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if group_by:
        chart_path = out_dir / f"delay_rate_by_{group_by}.png"
        save_delay_rate_chart(summary_df, group_by, chart_path)
        if chart_path.exists():
            print(f"Saved chart: {chart_path}")


if __name__ == "__main__":
    main()
