# layout.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container([
        dcc.Store(id="historical-data-store"),  # Stores fetched historical data (JSON)
        dbc.Row([
            dbc.Col(
                html.H5(
                    "Backtesting Dashboard",
                    className="mt-2",
                    style={
                        "fontFamily": "'Open Sans', sans-serif",
                        "fontWeight": "normal",
                        "fontSize": "1.5rem",
                        "color": "#aaa",
                        "textAlign": "left",
                        "marginLeft": "10px"
                    }
                ),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    [
                        html.H5("Common Parameters", style={"color": "white", "marginBottom": "10px"}),
                        html.Label("Symbol", style={"color": "white"}),
                        dcc.Dropdown(
                            id="symbol-dropdown",
                            options=[
                                {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                                {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                            ],
                            value="BTC/USDT",
                            clearable=False,
                            style={"backgroundColor": "#2c2f33", "color": "white"}
                        ),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Start Date", style={"color": "white"}),
                                dcc.DatePickerSingle(
                                    id="start-date-picker",
                                    date="2023-01-01"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("End Date", style={"color": "white"}),
                                dcc.DatePickerSingle(
                                    id="end-date-picker",
                                    date="2023-06-01"
                                )
                            ], width=6),
                        ]),
                        html.Br(),
                        html.Label("Timeframe", style={"color": "white"}),
                        dcc.Dropdown(
                            id="timeframe-dropdown",
                            options=[
                                {'label': '1m', 'value': '1m'},
                                {'label': '5m', 'value': '5m'},
                                {'label': '15m', 'value': '15m'},
                                {'label': '1h', 'value': '1h'},
                                {'label': '1d', 'value': '1d'},
                            ],
                            value="1h",
                            clearable=False,
                            style={"backgroundColor": "#2c2f33", "color": "white"}
                        ),
                        html.Br(),
                        html.Label("Strategy", style={"color": "white"}),
                        dcc.Dropdown(
                            id="strategy-dropdown",
                            options=[
                                {'label': 'WickFill Strategy', 'value': 'WickFillStrategy'},
                            ],
                            value="WickFillStrategy",
                            clearable=False,
                            style={"backgroundColor": "#2c2f33", "color": "white"}
                        ),
                        html.Br(),
                        dbc.Button("Run Strategy", id="run-strategy-button", color="secondary", n_clicks=0)
                    ],
                    style={
                        "backgroundColor": "#23272a",
                        "padding": "20px",
                        "border": "1px solid #444",
                        "borderRadius": "5px",
                        "marginTop": "50px",
                        "marginBottom": "30px"
                    }
                )
            ], width=4),
            dbc.Col([
                dcc.Graph(
                    id="candlestick-chart",
                    figure={
                        "data": [],
                        "layout": {
                            "paper_bgcolor": "#2c2f33",
                            "plot_bgcolor": "#2c2f33",
                            "xaxis": {"visible": False},
                            "yaxis": {"visible": False},
                            "title": {"text": "Loading chart...", "font": {"color": "white"}}
                        }
                    }
                ),
                html.Div(id="performance-metrics", className="mt-4", style={"textAlign": "left", "marginLeft": "20px"})
            ], width=8)
        ])
    ], fluid=True, style={
        "backgroundColor": "#2c2f33",
        "minHeight": "100vh",
        "padding": "20px"
    })
