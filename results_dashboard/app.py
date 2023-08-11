import dash
import dash_bootstrap_components as dbc
from results_dashboard import data
from dash import Dash, Input, Output, State, dcc, html

from results_dashboard.cache_manager import CacheSingleton
from results_dashboard.common_components import log_callback_trigger
from results_dashboard.test_selection import config_layout

cache = CacheSingleton()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    background_callback_manager=cache.background_callback_manager,
)

stores = [
    dcc.Store(id="test-id", storage_type="session"),
]


navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="https://www.frederickscompany.com/wp-content/themes/fredericks2021/images/the-fredericks-company-logo-2021.png",
                                height="30px",
                            )
                        ),
                        dbc.Col(dbc.NavbarBrand("Results Dashboard")),
                    ],
                    align="center",
                ),
                href="/",
                style={"text-decoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Test Selection", id="show-offcanvas")),
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem(
                                    "Angle Data", href="/data/angle_data"
                                ),
                            ],
                            label="Data",
                            nav=True,
                        ),
                        dbc.NavItem(dbc.NavLink("Over Time", href="/over_time/angle")),
                        dbc.NavItem(
                            dbc.NavLink("Repeatability", href="/repeatability/sensor")
                        ),
                    ],
                    className="ml-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
                is_open=False,
            ),
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
)


@app.callback(
    Output("config-offcanvas", "is_open"),
    Input("show-offcanvas", "n_clicks"),
    State("config-offcanvas", "is_open"),
    prevent_initial_call=True,
)
@log_callback_trigger
def toggle_config(n: int, is_open: bool) -> bool:
    return not is_open


@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
    prevent_initial_call=True,
)
@log_callback_trigger
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


app.layout = html.Div(
    [
        *data.initialize(app),
        *stores,
        navbar,
        dbc.Offcanvas(
            [
                config_layout,
            ],
            id="config-offcanvas",
            title="Test Selection",
            scrollable=True,
            is_open=False,
            style={"width": "50%"},
        ),
        dash.page_container,
    ],
    style={"padding": "20px"},
)


def docker_run() -> None:
    app.run_server(host="0.0.0.0")


if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=False)
