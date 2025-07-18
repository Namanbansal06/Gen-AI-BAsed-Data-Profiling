# generate_dashboard.py
import json
from charts_template import bar_chart, line_chart, pie_chart, donut_chart, radar_chart, scatter_chart, stacked_area_chart
import dp
import datetime

charts = dp.chart

# Generate HTML Template
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ECharts Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: Arial; background: #f9f9f9; padding: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; }}
        .chart {{ height: 400px; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 10px; }}
    </style>
</head>
<body>
    <h2>ECharts Dashboard</h2>
    <div class="grid">
        {divs}
    </div>

    <script>
        {scripts}
    </script>
</body>
</html>
'''

def convert(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    return str(obj)

# Generate DIVs and JS scripts
divs = ""
scripts = ""
for i, chart_dict in enumerate(charts):
    for chart_id, option in chart_dict.items():
        div_id = f"chart_{chart_id}_{i}"
        divs += f'<div id="{div_id}" class="chart"></div>\n'
        option_json = json.dumps(option, indent=2, default=convert)
        scripts += f'''
        var chart_{i} = echarts.init(document.getElementById('{div_id}'));
        chart_{i}.setOption({option_json});
        '''

# Final HTML
html_output = html_template.format(divs=divs, scripts=scripts)

# Write to file
with open("dashboard3.html", "w") as f:
    f.write(html_output)

print("✅ dashboard.html generated successfully!")
