import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, html

from results_dashboard.data.mongo import mongo_tilt_db

dash.register_page(__name__, path="/config")


def get_tests() -> pd.DataFrame:
    db = mongo_tilt_db()
    aggregate_query = [
        {"$sort": {"test_start_time": -1}},
        {
            "$project": {
                "label": {
                    "$concat": [
                        "$name",
                        "-",
                        {
                            "$dateToString": {
                                "date": "$test_start_time",
                                "format": "%m/%d/%Y-%H:%M:%S",
                            }
                        },
                    ]
                },
                "progress": {
                    "$divide": ["$status.steps_completed", "$status.total_steps"]
                },
                "rows_written": "$rows_written",
            }
        },
    ]
    test_df = pd.DataFrame(list(db["test"].aggregate(aggregate_query)))
    test_df["_id"] = test_df["_id"].astype(str)
    return test_df


layout = html.Div(
    [
        html.H1("Configuration"),
        dbc.Select(
            id="test-id-dropdown",
            options=[
                {"label": row["label"], "value": row["_id"]}
                for _, row in get_tests().iterrows()
            ],
            value=None,
            placeholder="Select a test",
        ),
        dbc.Button("Reset Session", id="reset-session", n_clicks=0, color="danger"),
    ]
)


@callback(
    Output("test-id", "value"),
    Output("test-id-dropdown", "value"),
    Input("test-id-dropdown", "value"),
    State("test-id", "value"),
)
def update_test_id(test_id: str, current_value: str) -> tuple[str, str]:
    if test_id is None:
        return current_value, current_value
    return test_id, test_id