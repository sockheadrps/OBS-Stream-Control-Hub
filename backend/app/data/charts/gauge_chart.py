import plotly.graph_objects as go

def create_gauge_chart(total_current_fuel, total_capacity):
    gauge_chart = go.Figure(go.Indicator(
        mode="gauge+number",
        value=(total_current_fuel / total_capacity) * 100,
        title={"text": "Total Fuel Percentage", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2},
            "bar": {"color": "blue"},
            "steps": [
                {"range": [0, 50], "color": "red"},
                {"range": [50, 80], "color": "yellow"},
                {"range": [80, 100], "color": "green"},
            ],
        },
    ))
    gauge_chart.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
    
    return gauge_chart