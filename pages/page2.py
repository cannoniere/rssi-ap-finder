from dash import html
import dash_bootstrap_components as dbc


def layout():
    return html.Div(
        children=[
            html.H2("Page 2"),
            html.P("This is the second page."),
            dbc.Button("Example Button", color="success"),
        ]
    )
