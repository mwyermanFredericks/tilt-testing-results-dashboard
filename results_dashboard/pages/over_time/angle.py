import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/over_time")

layout = html.Div(
    [
        html.H3("Angle Over Time"),
        html.Div(
            children=[
                dbc.Alert(
                    children=[
                        "No data available. Select a test in the ",
                        dcc.Link(
                            "Test Selection",
                            href="/config",
                            className="alert-link",
                        ),
                        " page.",
                    ],
                    color="warning",
                ),
            ],
            id="angle-over-time-graph",
        ),
    ]
)


@callback(
    Output("angle-over-time-graph", "children"),
    Input("angle-data", "data"),
)
def update_angle_over_time_graph(data: pd.DataFrame | None) -> html.Div:
    if data is None:
        raise PreventUpdate
    df = pd.DataFrame.from_records(data)
    if len(df) == 0:
        raise PreventUpdate
    # fig = px.line(
    #     df,
    #     x="sample_time",
    #     y="set_angle",
    #     title="Angle Over Time",
    # )
    # return fig
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
        )
    )
