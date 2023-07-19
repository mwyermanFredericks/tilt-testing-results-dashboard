import dash
from dash import dcc, html

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.H1("Tilt Results Dashboard"),
        html.P("This is the home page!"),
    ]
)
