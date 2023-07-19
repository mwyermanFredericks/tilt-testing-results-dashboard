import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from results_dashboard import data
from results_dashboard.views import config
from results_dashboard.views import data as data_view
from results_dashboard.views import over_time

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    html.Div(
        [
            data.get_div(app),
            config.get_div(app),
            data_view.get_div(app),
            over_time.get_div(app),
        ],
        style={
            "width": "1200px",
            "display": "inline-block",
            "padding": "20px",
            "text-align": "left",
        },
    ),
    style={"text-align": "center"},
)

if __name__ == "__main__":
    app.run(debug=False)
