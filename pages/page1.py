from dash import html
import dash_bootstrap_components as dbc


def layout():
    return html.Div(
        children=[
            html.H2("Page 1"),
            html.P("This is the first page."),
            dbc.Alert("Page 1 content goes here.", color="primary"),
        ]
    )
