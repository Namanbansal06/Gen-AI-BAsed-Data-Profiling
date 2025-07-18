import json
import datetime
from charts_template import bar_chart, line_chart, pie_chart, donut_chart, radar_chart, scatter_chart, stacked_area_chart
import dp

# Load charts from dp
charts = dp.chart

# Load profiling JSON
with open("sales_report.json") as f:
    profile = json.load(f)

columns_data = profile['variables']
correlations = profile.get("correlations", {})

# Format float stats nicely
def format_stat(value):
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)

stat_fields = [
    "min", "5%", "25%", "50%", "75%", "95%", "max", "range", "iqr",
    "mean", "std", "variance", "cv", "kurtosis", "skewness", "sum", "mad", "monotonic",
    "n_distinct", "p_distinct",
    "n_missing", "p_missing", "n_zeros", "p_zeros",
    "n_negative", "p_negative", "n_infinite", "p_infinite"
]

stat_cards_html = ''
for col_name, col_stats in columns_data.items():
    rows = ''
    for field in stat_fields:
        if field in col_stats:
            rows += f"<tr><td>{field}</td><td>{format_stat(col_stats[field])}</td></tr>"

    top_val = next(iter(col_stats.get("value_counts_index_sorted", {})), 'NA')
    samples = col_stats.get("first_rows", {})
    sample_vals = ', '.join(list(samples.values())[:3]) if isinstance(samples, dict) else 'NA'

    stat_cards_html += f'''
    <div class="card">
        <h3>{col_name}</h3>
        <p><strong>Type:</strong> {col_stats.get("type", "NA")}</p>
        <p><strong>Top Value:</strong> {top_val}</p>
        <p><strong>Sample:</strong> {sample_vals}</p>
        <table style="width:100%; font-size: 0.9em;">
            <thead><tr><th>Metric</th><th>Value</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''

def correlation_heatmap(title, data_list):
    columns = list(data_list[0].keys())
    matrix = [[row[col] for col in columns] for row in data_list]

    return {
        title: {
            "title": {"text": f"{title} Correlation", "left": "center"},
            "tooltip": {"position": "top"},
            "xAxis": {"type": "category", "data": columns, "axisLabel": {"rotate": 45}},
            "yAxis": {"type": "category", "data": columns},
            "visualMap": {
                "min": -1,
                "max": 1,
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "5%"
            },
            "series": [{
                "name": "correlation",
                "type": "heatmap",
                "data": [[j, i, round(matrix[i][j], 3)]
                         for i in range(len(matrix)) for j in range(len(matrix[i]))],
                "label": {"show": True},
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": 'rgba(0,0,0,0.5)'}}
            }]
        }
    }

if 'pearson' in correlations:
    charts.insert(0, correlation_heatmap("Pearson", correlations['pearson']))
if 'spearman' in correlations:
    charts.insert(1, correlation_heatmap("Spearman", correlations['spearman']))

def convert(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    return str(obj)

divs = ""
scripts = ""
for i, chart_dict in enumerate(charts):
    for chart_id, option in chart_dict.items():
        div_id = f"chart_{chart_id}_{i}"
        divs += f'''
        <div class="chart-wrapper">
            <button class="fullscreen-button" onclick="enlargeChart('{div_id}')">🔍</button>
            <div id="{div_id}" class="chart"></div>
        </div>
        '''
        option_json = json.dumps(option, indent=2, default=convert)
        scripts += f'''
        var chart_{i} = echarts.init(document.getElementById('{div_id}'));
        chart_{i}.setOption({option_json});
        '''

html_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ECharts Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f9f9f9; padding: 20px; }}
        h2 {{ margin-top: 0; }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            max-height: 400px;
            overflow-y: auto;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }}
        .chart-wrapper {{
            position: relative;
        }}
        .chart {{
            height: 400px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            padding: 10px;
        }}
        .fullscreen-button {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 100;
            background-color: #ffffffcc;
            border: none;
            cursor: pointer;
            padding: 6px 10px;
            border-radius: 5px;
            font-size: 16px;
        }}
        #fullscreenModal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        #fullscreenChart {{
            width: 90vw;
            height: 90vh;
        }}
        #exitButton {{
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 28px;
            color: white;
            background: none;
            border: none;
            cursor: pointer;
            z-index: 10001;
        }}
    </style>
</head>
<body>
    <h2>ECharts Dashboard</h2>

    <div class="cards">
        {cards}
    </div>

    <div class="grid">
        {divs}
    </div>

    <script>
        {scripts}

        let currentFullscreenChart = null;

        function enlargeChart(chartId) {{
            const original = echarts.getInstanceByDom(document.getElementById(chartId));
            const option = original.getOption();

            const existing = document.getElementById('fullscreenModal');
            if (existing) existing.remove();

            const modal = document.createElement('div');
            modal.id = 'fullscreenModal';

            const exitBtn = document.createElement('button');
            exitBtn.id = 'exitButton';
            exitBtn.innerText = '❌';
            exitBtn.onclick = exitFullscreen;

            const chartDiv = document.createElement('div');
            chartDiv.id = 'fullscreenChart';

            modal.appendChild(exitBtn);
            modal.appendChild(chartDiv);
            document.body.appendChild(modal);

            currentFullscreenChart = echarts.init(chartDiv);
            currentFullscreenChart.setOption(option);
        }}

        function exitFullscreen() {{
            const modal = document.getElementById('fullscreenModal');
            if (modal) {{
                if (currentFullscreenChart) {{
                    currentFullscreenChart.dispose();
                    currentFullscreenChart = null;
                }}
                modal.remove();
            }}
        }}

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                exitFullscreen();
            }}
        }});
    </script>
</body>
</html>
'''

html_output = html_template.format(cards=stat_cards_html, divs=divs, scripts=scripts)

with open("dashboard2.html", "w") as f:
    f.write(html_output)

print("✅ dashboard2.html with fullscreen support added successfully!")
