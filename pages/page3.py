from dash import html
import dash_bootstrap_components as dbc


def layout():
    return html.Div(
        children=[
            html.H2("Page 3"),
            html.P("This is the third page."),
            dbc.Card(
                dbc.CardBody("This is a Bootstrap card inside Page 3."),
                className="mt-3",
            ),
        ]
    )
