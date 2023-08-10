import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dcc, html

from results_dashboard.common_components import log_callback_trigger
from results_dashboard.data.mongo import mongo_tilt_db

TEST_ID_NO_SELECTION_TEXT = "Select a test"


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
    res = db["test"].aggregate(aggregate_query)
    res_list = list(res)
    test_df = pd.DataFrame(res_list)
    test_df["_id"] = test_df["_id"].astype(str)
    return test_df


config_layout = html.Div(
    [
        html.H1("Configuration"),
        dbc.Select(
            id="test-id-dropdown",
            options=[{"label": TEST_ID_NO_SELECTION_TEXT, "value": None}]
            + [
                {"label": row["label"], "value": row["_id"]}
                for _, row in get_tests().iterrows()
            ],
            value=None,
            placeholder="Select a test",
        ),
    ]
)


@callback(
    [Output("test-id", "data"), Output("test-id-dropdown", "value")],
    [Input("test-id-dropdown", "value")],
    [State("test-id", "data")],
)
@log_callback_trigger
def update_test_id(
    test_id_dropdown: str | None, test_id_store: str | None
) -> tuple[str | None, str | None]:
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"] == "test-id-dropdown.value":
        return test_id_dropdown, test_id_dropdown
    else:
        return test_id_store, test_id_store


# @callback(
#     Output("test-id", "data"),
#     Input("test-id-dropdown", "value"),
#     prevent_initial_call=True,
# )
# @log_callback_trigger
# def update_test_id(test_id_dropdown: str | None) -> str | None:
#     return test_id_dropdown
