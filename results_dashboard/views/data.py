import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, html
from dash.exceptions import PreventUpdate


def get_div(app: Dash) -> html.Div:
    create_callbacks(app)

    return html.Div(
        [
            html.H1("Data", style={"textAlign": "center"}),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Angle Data"),
                            html.Div(
                                id="angle-data-table",
                                style={"overflow": "scroll", "height": "20vh"},
                            ),
                        ],
                    ),
                ]
            ),
        ]
    )


def create_callbacks(app: Dash) -> None:
    @app.callback(
        Output("angle-data-table", "children"),
        Input("angle-data", "data"),
    )
    def update_angle_data_table(data: pd.DataFrame | None) -> html.Table:
        if data is None:
            raise PreventUpdate
        df = pd.DataFrame.from_records(data)
        df = df.drop(columns=["_id"])
        if len(df) == 0:
            raise PreventUpdate

        table = dbc.Table(
            [html.Tr([html.Th(col) for col in df.columns])]
            + [
                html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
                for i in range(min(len(df), 500))  # only show first 500 rows
            ]
        )
        return table
