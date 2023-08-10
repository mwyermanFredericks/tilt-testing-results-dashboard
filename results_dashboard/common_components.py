import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html

select_test_alert = dbc.Alert(
    children=[
        "No test is selected. Please select a test from the dropdown menu.",
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


def log_callback_trigger(callback_func):
    def wrapper(*args, **kwargs):
        ctx = dash.callback_context
        s = f"Callback Function: {callback_func.__name__}"
        s += f"\n  Triggered by: {ctx.triggered[0]['prop_id']}"
        for arg in args:
            s += f"\n  arg: {arg}"
        for key, value in kwargs.items():
            s += f"\n  kwarg: {key}={value}"
        print(s)
        return callback_func(*args, **kwargs)

    return wrapper


__all__ = [
    "select_test_alert",
    "no_data_alert",
    "get_alert_from_data",
    "log_callback_trigger",
]
