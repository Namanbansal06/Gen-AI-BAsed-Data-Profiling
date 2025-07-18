import json
import os
import re
import google.generativeai as genai
from pyspark.sql import SparkSession

# Step 1: Create Spark session and load CSV
spark = SparkSession.builder.appName("Top10RowsAsString").getOrCreate()

csv_file_path = "sample2.csv"
df = spark.read.option("header", True).csv(csv_file_path)

# Step 2: Collect top 10 rows
top10 = df.limit(10).collect()
top10_str = "\n".join([str(row.asDict()) for row in top10])
print("✅ Top 10 rows extracted.")

# Step 3: Configure Gemini API
genai.configure(api_key="AIzaSyBzkoYf6LzFjBP-1pRS5wd69HL_NEIByqs")
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# Step 4: Prompt Gemini
prompt = f"""
You are a data visualization assistant.
The dataset is stored in the variable `top10_str` as plain text.
You need to analyze its schema and suggest at least 15 charts based on the data.
Use only the following chart types:
bar_chart, line_chart, pie_chart, scatter_chart, radar_chart, donut_chart, stacked_area_chart.
For each chart, create a JSON object with the following keys:
- column_1: the primary column used in the chart
- column_2: set this to null if the chart is based on only one column
- chart_type: one of the allowed chart types
- title: a clear and relevant title for the chart

Important:
- The following chart types must have non-null values in both column_1 and column_2:
  bar_chart, line_chart, radar_chart, stacked_area_chart.
- The following chart types can have null in column_2:
  pie_chart, donut_chart, scatter_chart.
- Return only a JSON array of chart suggestions, nothing else.
- Focus on both single-column and inter-column relationships.

Now analyze the dataset below and return the chart suggestions as per the instructions:

{top10_str}
"""

# Step 5: Generate response
response = model.generate_content(prompt)
print("✅ Response received from Gemini.")

# Step 6: Extract and validate JSON
try:
    # Extract JSON from the response (assumes response.text is valid JSON array)
    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
    chart_suggestions = json.loads(json_match.group()) if json_match else []
except Exception as e:
    print(f"❌ Failed to parse JSON from model response: {e}")
    chart_suggestions = []

# Step 7: Validate charts
valid_chart_types_requiring_column2 = {
    "bar_chart", "line_chart", "radar_chart", "stacked_area_chart"
}

validated_charts = []
for chart in chart_suggestions:
    chart_type = chart.get("chart_type")
    if chart_type in valid_chart_types_requiring_column2 and chart.get("column_2") is None:
        print(f"⚠️ Skipping invalid chart (missing column_2 for {chart_type}): {chart}")
        continue
    validated_charts.append(chart)

# Step 8: Save the validated JSON
json_file_name = os.path.splitext(os.path.basename(csv_file_path))[0] + ".json"
with open(json_file_name, 'w') as f:
    json.dump(validated_charts, f, indent=2)

print(f"✅ Saved {len(validated_charts)} validated charts to {json_file_name}")
