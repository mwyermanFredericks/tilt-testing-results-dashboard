import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import callback, dcc, html

from results_dashboard.common_components import get_alert_from_data

dash.register_page(__name__, path="/repeatability/sensor")


layout = html.Div(
    [
        dbc.Spinner(
            html.Div(
                id="sensor-repeatability-graph",
            ),
            color="dark",
        )
    ]
)


@callback(
    dash.Output("sensor-repeatability-graph", "children"),
    dash.Input("sensor-repeatability-data", "data"),
)
def update_sensor_repeatability_graph(data: pd.DataFrame | None) -> html.Div:
    import time

    time.sleep(1)
    if (alert := get_alert_from_data(data)) is not None:
        return alert
    df = pd.DataFrame.from_records(data)
    return html.Div(
        dcc.Graph(
            figure=px.line(
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
            ),
        )
    )
