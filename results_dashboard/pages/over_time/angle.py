import dash
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

from results_dashboard.common_components import get_alert_from_data

dash.register_page(__name__, path="/over_time/angle")

layout = html.Div(
    [
        html.Div(
            id="angle-over-time-graph",
        ),
    ]
)


@callback(
    Output("angle-over-time-graph", "children"),
    Input("angle-data", "data"),
)
def update_angle_over_time_graph(data: pd.DataFrame | None) -> html.Div:
    if (alert := get_alert_from_data(data)) is not None:
        return alert
    df = pd.DataFrame.from_records(data)
    return html.Div(
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Scatter(
                        x=df["sample_time"],
                        y=df["set_angle"],
                        mode="lines",
                        name="set_angle",
                    ),
                ],
                layout=go.Layout(
                    title="Angle Over Time",
                    xaxis={"title": "Time"},
                    yaxis={"title": "Angle (deg)"},
                    legend={"x": 0, "y": 1},
                    hovermode="closest",
                ),
            ),
        ),
    )
