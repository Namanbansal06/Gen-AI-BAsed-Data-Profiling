import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import datetime
from charts_template import (
    bar_chart, line_chart, pie_chart, donut_chart,
    radar_chart, scatter_chart, stacked_area_chart
)

# Initialize Spark
spark = SparkSession.builder.appName("ChartDashboard").getOrCreate()

# Load Data
df = spark.read.csv("sales_data.csv", header=True, inferSchema=True)
df.printSchema()

# Load chart spec JSON
with open("sales_data.json", "r") as f:
    chart_specs = json.load(f)

# Define aggregation function
def get_aggregation_df(df, col1, col2, agg_type, limit=30):
    if agg_type == "value_count":
        return df.groupBy(col1).agg(count("*").alias("value")).orderBy(desc("value")).dropna().limit(limit)
    elif agg_type == "count":
        return df.groupBy(col1).agg(count(col2).alias("value")).orderBy(desc("value")).dropna().limit(limit)
    elif agg_type == "sum":
        return df.groupBy(col1).agg(sum(col2).alias("value")).orderBy(desc("value")).dropna().limit(limit)
    elif agg_type == "mean":
        return df.groupBy(col1).agg(avg(col2).alias("value")).orderBy(desc("value")).dropna().limit(limit)
    elif agg_type == "median":
        return df.groupBy(col1).agg(expr(f"percentile_approx({col2}, 0.5)").alias("value")).orderBy(desc("value")).dropna().limit(limit)
    elif agg_type == "min":
        return df.groupBy(col1).agg(min(col2).alias("value")).orderBy(desc("value")).dropna().limit(limit)
    elif agg_type == "max":
        return df.groupBy(col1).agg(max(col2).alias("value")).orderBy(desc("value")).dropna().limit(limit)
    return None

chart = []

for spec in chart_specs:
    col1 = spec.get('column_1')
    col2 = spec.get('column_2')
    chart_type = spec.get('chart_type')
    title = spec.get('title')

    # Handle pie/donut charts (only col1 required)
    if chart_type in ["pie_chart", "donut_chart"]:
        grouped_df = df.groupBy(col1).agg(count("*").alias("value")).dropna().limit(50)
        data = [{"name": row[col1], "value": row["value"]} for row in grouped_df.collect()]
        chart_func = pie_chart if chart_type == "pie_chart" else donut_chart
        chart.append({chart_type.replace("_chart", ""): chart_func(title, data)})
        continue

    # Skip invalid specs (col2 required for other types)
    if not col1 or not col2:
        continue

    base_chart = chart_type.split("_")[0]
    family_type = chart_type.replace(f"{base_chart}_", "")  # e.g., 'bar_chart'

    # Handle metric-based charts
    if family_type in ["bar_chart", "line_chart", "radar_chart", "scatter_chart", "stacked_area_chart"]:
        grouped_df = get_aggregation_df(df, col1, col2, base_chart)
        if not grouped_df:
            continue
        rows = grouped_df.collect()
        x = [row[col1] for row in rows]
        y = [row["value"] for row in rows]

        if family_type == "bar_chart":
            chart.append({base_chart: bar_chart(title, x, y)})

        elif family_type == "line_chart":
            chart.append({"line": line_chart(title, x, y)})

        elif family_type == "radar_chart":
            chart.append({base_chart: radar_chart(title, x, y)})

        elif family_type == "scatter_chart":
            points = list(zip(range(len(x)), y))  # index vs y-value
            chart.append({base_chart: scatter_chart(title, points)})

        elif family_type == "stacked_area_chart":
            x_vals = [str(val) for val in x]
            series = [{"name": title, "data": y}]
            chart.append({base_chart: stacked_area_chart(title, x_vals, series)})

    # Handle base charts without prefix
    elif chart_type == "bar_chart":
        grouped_df = df.groupBy(col1).agg(count("*").alias("value")).dropna().limit(30)
        x = [row[col1] for row in grouped_df.collect()]
        y = [row["value"] for row in grouped_df.collect()]
        chart.append({"bar": bar_chart(title, x, y)})

    elif chart_type == "line_chart":
        grouped_df = df.groupBy(col1).agg(count("*").alias("value")).dropna().orderBy(col1).limit(30)
        x = [row[col1] for row in grouped_df.collect()]
        y = [row["value"] for row in grouped_df.collect()]
        chart.append({"line": line_chart(title, x, y)})

    elif chart_type == "radar_chart":
        grouped_df = df.groupBy(col1).agg(count("*").alias("value")).dropna().limit(30)
        x = [row[col1] for row in grouped_df.collect()]
        y = [row["value"] for row in grouped_df.collect()]
        chart.append({"radar": radar_chart(title, x, y)})

    elif chart_type == "scatter_chart":
        grouped_df = df.groupBy(col1, col2).agg(count("*").alias("value")).dropna().limit(50)
        points = [[row[col1], row["value"]] for row in grouped_df.collect()]
        chart.append({"scatter": scatter_chart(title, points)})

    elif chart_type == "stacked_area_chart":
        grouped = df.groupBy(col1, col2).agg(count("*").alias("value")).dropna().limit(50)
        rows = grouped.collect()
        x_labels = sorted(list(set([row[col1] for row in rows])))
        y_keys = sorted(list(set([row[col2] for row in rows])))

        series = []
        for k in y_keys:
            data_map = {row[col1]: row["value"] for row in rows if row[col2] == k}
            series.append({
                "name": k,
                "data": [data_map.get(label, 0) for label in x_labels]
            })

        chart.append({'stacked_area': stacked_area_chart(title, x_labels, series)})

# Optional: Save charts or visualize
# print(json.dumps(chart, indent=2))

