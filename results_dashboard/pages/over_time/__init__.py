from dash import Dash, dcc, html

from results_dashboard.views.over_time import angle


def get_div(app: Dash) -> html.Div:
    angle.create_callbacks(app)

    return html.Div(
        [
            html.H1("Over Time", style={"textAlign": "center"}),
            html.Div(
                [
                    dcc.Graph(id="angle-over-time-graph"),
                ],
            ),
        ]
    )
