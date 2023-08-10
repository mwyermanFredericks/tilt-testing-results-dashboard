import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, dash_table, dcc, html

from results_dashboard.common_components import get_alert_from_data

dash.register_page(__name__, path="/data/angle_data")


layout = html.Div(
    [
        html.Div(
            id="angle-data-table",
        ),
    ]
)


@callback(
    Output("angle-data-table", "children"),
    Input("angle-data", "data"),
)
def update_angle_data_table(data: pd.DataFrame | None) -> html.Div:
    if (alert := get_alert_from_data(data)) is not None:
        return alert
    df = pd.DataFrame.from_records(data)
    df = df.drop(columns=["_id"])

    table = dash_table.DataTable(
        id="angle-data-table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        style_cell={"textAlign": "left"},
        style_header={
            "backgroundColor": "rgb(230, 230, 230)",
            "fontWeight": "bold",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "rgb(248, 248, 248)",
            },
        ],
        style_table={
            "overflowX": "auto",
            "overflowY": "auto",
            "height": "80vh",
            "padding": "10px",
        },
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


# @callback(
#     Output("download-angle-data-csv", "data"),
#     Input("download-angle-data-button", "n_clicks"),
#     State("angle-data", "data"),
#     prevent_initial_call=True,
#     suppress_callback_exceptions=True,
# )
# def download_angle_data_csv(n_clicks: int, data: pd.DataFrame | None) -> object:
#     df = pd.DataFrame.from_records(data)
#     return dcc.send_data_frame(df.to_csv, filename="angle_data.csv")
