import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import callback, dcc, html

from results_dashboard.common_components import get_alert_from_data

dash.register_page(__name__, path="/repeatability/sensor")


layout = html.Div(
    [
        html.Div(
            id="sensor-repeatability-settings-form",
            children=[
                dbc.Label("Repeatability Graph Upper Limit"),
                dbc.Input(
                    id="sensor-repeatability-max-y-axis",
                    type="number",
                    value=None,
                    step=0.0001,
                    min=0.0001,
                ),
                dbc.Label("Expected Repeatability"),
                dbc.Input(
                    id="sensor-repeatability-expected-repeatability",
                    type="number",
                    value=None,
                    step=0.0001,
                    min=0.0001,
                ),
                dbc.Label("Sensor Range"),
                dbc.Input(
                    id="sensor-repeatability-sensor-range",
                    type="number",
                    value=None,
                    step=0.0001,
                    min=0.0001,
                ),
            ],
        ),
        dbc.Spinner(
            html.Div(
                id="sensor-repeatability-graph",
            ),
            color="dark",
        ),
    ]
)


@callback(
    dash.Output("sensor-repeatability-graph", "children"),
    [
        dash.Input("sensor-repeatability-data", "data"),
        dash.Input("sensor-repeatability-max-y-axis", "value"),
        dash.Input("sensor-repeatability-expected-repeatability", "value"),
        dash.Input("sensor-repeatability-sensor-range", "value"),
    ],
)
def update_sensor_repeatability_graph(
    data: pd.DataFrame | None,
    max_y: float | None,
    expected_repeatability: float | None,
    sensor_range: float | None,
) -> html.Div:
    if (alert := get_alert_from_data(data)) is not None:
        return alert
    df = pd.DataFrame.from_records(data)
    fig = px.line(
        df,
        x="set_angle",
        y="repeatability",
        color="sensor_name",
        title="Sensor Repeatability",
        labels={
            "set_angle": "Set Angle (deg)",
            "repeatability": "Repeatability (+/- deg)",
            "sensor_name": "Sensor",
        },
    )
    if max_y:
        fig.update_yaxes(range=[0, max_y])
    if sensor_range:
        fig.update_xaxes(range=[-sensor_range, sensor_range])
    if expected_repeatability:
        fig.add_hline(
            y=expected_repeatability,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Expected Repeatability: {expected_repeatability:.4f} deg",
        )
    return html.Div(dcc.Graph(figure=fig))
