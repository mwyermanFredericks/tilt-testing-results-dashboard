import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, Input, Output
from dash.exceptions import PreventUpdate


def create_callbacks(app: Dash) -> None:
    @app.callback(
        Output("angle-over-time-graph", "figure"),
        Input("angle-data", "data"),
    )
    def update_angle_over_time_graph(data: pd.DataFrame | None) -> go.Figure:
        if data is None:
            raise PreventUpdate
        df = pd.DataFrame.from_records(data)
        if len(df) == 0:
            raise PreventUpdate
        fig = px.line(
            df,
            x="sample_time",
            y="set_angle",
            title="Angle Over Time",
        )
        return fig
