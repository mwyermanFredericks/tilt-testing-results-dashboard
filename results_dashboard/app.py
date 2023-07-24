import dash
import dash_bootstrap_components as dbc
import data
from dash import Dash, Input, Output, State, dcc, html

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)


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
                        dbc.NavItem(dbc.NavLink("Test Selection", href="/config")),
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
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


app.layout = html.Div(
    [
        *data.initialize(app),
        *stores,
        navbar,
        dash.page_container,
    ],
    style={"padding": "20px"},
)


if __name__ == "__main__":
    app.run(debug=False)
