# # Chart Template Generator Functions

# def bar_chart(title, x_data, y_data, series_name="Series"):
#     return {
#         "title": {"text": title},
#         "tooltip": {},
#         "xAxis": {"type": "category", "data": x_data},
#         "yAxis": {"type": "value"},
#         "series": [{
#             "name": series_name,
#             "type": "bar",
#             "data": y_data
#         }]
#     }


# def line_chart(title, x_data, y_data, series_name="Series"):
#     return {
#         "title": {"text": title},
#         "tooltip": {"trigger": "axis"},
#         "xAxis": {"type": "category", "data": x_data},
#         "yAxis": {"type": "value"},
#         "series": [{
#             "name": series_name,
#             "type": "line",
#             "data": y_data
#         }]
#     }


# def pie_chart(title, data, radius="50%"):
#     """
#     data = [{"name": "A", "value": 30}, {"name": "B", "value": 70}]
#     """
#     return {
#         "title": {"text": title, "left": "center"},
#         "tooltip": {"trigger": "item"},
#         "series": [{
#             "type": "pie",
#             "radius": radius,
#             "data": data,
#             "emphasis": {
#                 "itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0, 0, 0, 0.5)"}
#             }
#         }]
#     }


# def scatter_chart(title, data, x_name="X", y_name="Y"):
#     """
#     data = [[x1, y1], [x2, y2], ...]
#     """
#     return {
#         "title": {"text": title},
#         "tooltip": {},
#         "xAxis": {"name": x_name},
#         "yAxis": {"name": y_name},
#         "series": [{
#             "symbolSize": 10,
#             "data": data,
#             "type": "scatter"
#         }]
#     }


# def radar_chart(title, indicators, values, series_name="Series"):
#     """
#     indicators = [{"name": "Metric1", "max": 100}, ...]
#     values = [value1, value2, ...]
#     """
#     return {
#         "title": {"text": title},
#         "tooltip": {},
#         "radar": {"indicator": indicators},
#         "series": [{
#             "name": series_name,
#             "type": "radar",
#             "data": [{"value": values, "name": series_name}]
#         }]
#     }


# def donut_chart(title, data, inner_radius="40%", outer_radius="70%"):
#     """
#     data = [{"name": "A", "value": 30}, {"name": "B", "value": 70}]
#     """
#     return {
#         "title": {"text": title, "left": "center"},
#         "tooltip": {"trigger": "item"},
#         "series": [{
#             "type": "pie",
#             "radius": [inner_radius, outer_radius],
#             "avoidLabelOverlap": False,
#             "data": data,
#             "emphasis": {
#                 "itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0, 0, 0, 0.5)"}
#             }
#         }]
#     }


# def stacked_area_chart(title, x_data, series_data):
#     """
#     series_data = [{"name": "A", "data": [10,20,30]}, {"name": "B", "data": [5,15,25]}]
#     """
#     return {
#         "title": {"text": title},
#         "tooltip": {"trigger": "axis"},
#         "legend": {"data": [s["name"] for s in series_data]},
#         "xAxis": {"type": "category", "boundaryGap": False, "data": x_data},
#         "yAxis": {"type": "value"},
#         "series": [
#             {
#                 "name": s["name"],
#                 "type": "line",
#                 "stack": "Total",
#                 "areaStyle": {},
#                 "data": s["data"]
#             } for s in series_data
#         ]
#     }


# Chart Template Generator Functions with Dynamic Y-Axis Support

import math

def get_y_axis_config(y_values):
    if not y_values:
        return {"type": "value"}

    y_min = min(y_values)
    y_max = max(y_values)

    # Handle case where all values are equal
    if y_min == y_max:
        return {
            "type": "value",
            "min": y_min - 1,
            "max": y_max + 1
        }

    padding = (y_max - y_min) * 0.1
    y_min_adj = y_min - padding
    y_max_adj = y_max + padding

    # Determine rounding base
    range_span = y_max_adj - y_min_adj
    rounding_base = 10 ** int(math.floor(math.log10(range_span)))  # e.g., 100, 10, 1, 0.1, etc.

    # Round min down and max up to nearest rounding_base
    y_min_final = math.floor(y_min_adj / rounding_base) * rounding_base
    y_max_final = math.ceil(y_max_adj / rounding_base) * rounding_base

    return {
        "type": "value",
        "min": y_min_final,
        "max": y_max_final
    }

def bar_chart(title, x_data, y_data, series_name="Series"):
    return {
        "title": {"text": title},
        "tooltip": {},
        "xAxis": {"type": "category", "data": x_data},
        "yAxis": get_y_axis_config(y_data),
        "series": [{
            "name": series_name,
            "type": "bar",
            "data": y_data
        }]
    }

def line_chart(title, x_data, y_data, series_name="Series"):
    return {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": x_data},
        "yAxis": get_y_axis_config(y_data),
        "series": [{
            "name": series_name,
            "type": "line",
            "data": y_data
        }]
    }

def pie_chart(title, data, radius="50"):
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [{
            "type": "pie",
            "radius": radius,
            "data": data,
            "emphasis": {
                "itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0, 0, 0, 0.5)"}
            }
        }]
    }

def scatter_chart(title, data, x_name="X", y_name="Y"):
    y_data = [point[1] for point in data]
    return {
        "title": {"text": title},
        "tooltip": {},
        "xAxis": {"name": x_name},
        "yAxis": get_y_axis_config(y_data) | {"name": y_name},
        "series": [{
            "symbolSize": 10,
            "data": data,
            "type": "scatter"
        }]
    }

def radar_chart(title, indicators, values, series_name="Series"):
    return {
        "title": {"text": title},
        "tooltip": {},
        "radar": {"indicator": indicators},
        "series": [{
            "name": series_name,
            "type": "radar",
            "data": [{"value": values, "name": series_name}]
        }]
    }

def donut_chart(title, data, inner_radius="40%", outer_radius="70%"):
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [{
            "type": "pie",
            "radius": [inner_radius, outer_radius],
            "avoidLabelOverlap": False,
            "data": data,
            "emphasis": {
                "itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0, 0, 0, 0.5)"}
            }
        }]
    }

def stacked_area_chart(title, x_data, series_data):
    all_y_values = [v for s in series_data for v in s["data"]]
    return {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": [s["name"] for s in series_data]},
        "xAxis": {"type": "category", "boundaryGap": False, "data": x_data},
        "yAxis": get_y_axis_config(all_y_values),
        "series": [
            {
                "name": s["name"],
                "type": "line",
                "stack": "Total",
                "areaStyle": {},
                "data": s["data"]
            } for s in series_data
        ]
    }