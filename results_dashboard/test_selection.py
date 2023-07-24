import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dcc, html

from results_dashboard.data.mongo import mongo_tilt_db


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


config_layout = html.Div(
    [
        html.H1("Configuration"),
        dbc.Select(
            id="test-id",
            options=[
                {"label": row["label"], "value": row["_id"]}
                for _, row in get_tests().iterrows()
            ],
            value=None,
            placeholder="Select a test",
            persistence=True,
            persistence_type="session",
        ),
        dbc.Button("Reset Session", id="reset-session", n_clicks=0, color="danger"),
    ]
)


# @callback(
#     Output("test-id", "value"),
#     [Input("reset-session", "n_clicks")],
# )
# def reset_session(n_clicks: int) -> str | None:
#     print("reset_session", n_clicks)
#     if n_clicks > 0:
#         return None
#     return dash.no_update
