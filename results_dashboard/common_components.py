import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

select_test_alert = dbc.Alert(
    children=[
        "No data available. Select a test from the ",
        dcc.Link(
            "Test Selection",
            href="/config",
            className="alert-link",
        ),
        " page.",
    ],
    color="warning",
)

no_data_alert = dbc.Alert(
    children=["No data is available for the selected test."],
    color="warning",
)


def get_alert_from_data(data: pd.DataFrame | None) -> html.Div | None:
    if data is None:
        return html.Div(select_test_alert)
    elif len(data) == 0:
        return html.Div(no_data_alert)
    return None


__all__ = [
    "select_test_alert",
    "no_data_alert",
    "get_alert_from_data" "spinner",
]
