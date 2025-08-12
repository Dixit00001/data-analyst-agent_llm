import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def encode_plot_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def run_pipeline(questions_file, data_files):
    df = pd.read_csv(data_files[0])

    if not all(col in df.columns for col in ["Region", "Sales", "Date"]):
        raise ValueError("CSV must have 'Region', 'Sales', and 'Date' columns")

    total_sales = df["Sales"].sum()
    top_region = df.groupby("Region")["Sales"].sum().idxmax()
    day_sales_correlation = df["Date"].apply(lambda x: pd.to_datetime(x).day).corr(df["Sales"])
    median_sales = df["Sales"].median()
    total_sales_tax = total_sales * 0.10

    sales_by_region = df.groupby("Region")["Sales"].sum()
    sales_by_region.plot(kind="bar", color="blue")
    plt.title("Total Sales by Region")
    plt.xlabel("Region")
    plt.ylabel("Total Sales")
    bar_chart_b64 = encode_plot_to_base64()

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["CumulativeSales"] = df["Sales"].cumsum()
    plt.plot(df["Date"], df["CumulativeSales"], color="red")
    plt.title("Cumulative Sales Over Time")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Sales")
    cumulative_sales_chart_b64 = encode_plot_to_base64()

    return {
        "total_sales": float(round(total_sales, 2)),
        "top_region": str(top_region),
        "day_sales_correlation": float(round(day_sales_correlation, 4)),
        "bar_chart": bar_chart_b64,
        "median_sales": float(round(median_sales, 2)),
        "total_sales_tax": float(round(total_sales_tax, 2)),
        "cumulative_sales_chart": cumulative_sales_chart_b64
    }
