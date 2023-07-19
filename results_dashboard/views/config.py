import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, State, dcc, exceptions, html

from results_dashboard.data.mongo import mongo_tilt_db


def get_tests():
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


def get_div(app: Dash) -> html.Div:
    @app.callback(
        Output("settings-modal", "is_open"),
        [Input("open-settings", "n_clicks"), Input("close-settings", "n_clicks")],
        State("settings-modal", "is_open"),
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output("test-ids", "value"),
        [Input("test-dropdown", "value"), Input("close-settings", "n_clicks")],
        State("test-ids", "value"),
    )
    def update_settings(test_ids, n_clicks, current_test_ids):
        if n_clicks:
            return test_ids
        raise exceptions.PreventUpdate

    # just have a button to open a modal with settings
    return html.Div(
        [
            dcc.Store(id="test-ids", data=[]),
            dbc.Button(
                "Settings",
                id="open-settings",
                className="mr-1",
                color="primary",
                outline=True,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader("Settings"),
                    dbc.ModalBody(
                        [
                            dcc.Dropdown(
                                id="test-dropdown",
                                options=[
                                    {
                                        "label": row["label"],
                                        "value": row["_id"],
                                    }
                                    for _, row in get_tests().iterrows()
                                ],
                                value=None,
                                multi=True,
                                placeholder="Select a test",
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-settings", className="ml-auto")
                    ),
                ],
                id="settings-modal",
                is_open=False,
            ),
        ],
        style={"textAlign": "center"},
        className="mt-3",
    )
    # [
    #     dcc.Dropdown(
    #         id="test-dropdown",
    #         options=[
    #             {"label": row["label"], "value": row["_id"]}
    #             for _, row in get_tests().iterrows()
    #         ],
    #         value=None,
    #         multi=True,
    #         placeholder="Select a test",
    #     ),
    # ]
    # )
