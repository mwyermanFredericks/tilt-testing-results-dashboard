import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/data/angle_data")


layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Angle Data"),
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
                            id="angle-data-table",
                        ),
                    ],
                ),
            ]
        ),
    ]
)


@callback(
    Output("angle-data-table", "children"),
    Input("angle-data", "data"),
)
def update_angle_data_table(data: pd.DataFrame | None) -> html.Div:
    if data is None:
        raise PreventUpdate
    df = pd.DataFrame.from_records(data)
    if len(df) == 0:
        raise PreventUpdate

    table = dbc.Table(
        [html.Tr([html.Th(col) for col in df.columns])]
        + [
            html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
            for i in range(len(df))
        ],
        bordered=True,
    )

    download_button = dbc.Button(
        "Download CSV",
        id="download-angle-data-button",
        color="primary",
        className="mr-1",
        n_clicks=0,
    )

    return html.Div(
        [table, dcc.Download(id="download-angle-data-csv"), download_button]
    )


@callback(
    Output("download-angle-data-csv", "data"),
    Input("download-angle-data-button", "n_clicks"),
    Input("angle-data", "data"),
    prevent_initial_call=True,
)
def download_angle_data_csv(n_clicks: int, data: pd.DataFrame | None) -> object:
    df = pd.DataFrame.from_records(data)
    return dcc.send_data_frame(df.to_csv, filename="angle_data.csv")
