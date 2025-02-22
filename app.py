# app.py
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import datetime
import pandas as pd
import logging

from data_fetcher import DataFetcher
from strategies import WickFillStrategy  # Currently available strategy.
from backtester import backtest_strategy
from plot_utils import create_candlestick_figure, add_trade_markers
from strategy_settings import STRATEGY_SETTINGS
from layout import create_layout

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the data fetcher.
data_fetcher_instance = DataFetcher()

# Use the DARKLY theme for a modern dark look.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Backtesting Dashboard"
app.layout = create_layout()

# Combined callback:
# - When any common parameter changes (or on initial load), load/update the chart.
# - When "Run Strategy" is clicked, overlay strategy results.
@app.callback(
    [Output("candlestick-chart", "figure"),
     Output("historical-data-store", "data"),
     Output("performance-metrics", "children")],
    [Input("symbol-dropdown", "value"),
     Input("start-date-picker", "date"),
     Input("end-date-picker", "date"),
     Input("timeframe-dropdown", "value"),
     Input("strategy-dropdown", "value"),
     Input("run-strategy-button", "n_clicks")],
    [State("historical-data-store", "data"),
     State("candlestick-chart", "figure")]
)
def update_dashboard(symbol, start_date, end_date, timeframe, strategy_name, run_clicks, stored_data, current_fig):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    logger.info("Triggered by: %s", trigger_id)

    # If the "Run Strategy" button was clicked:
    if trigger_id == "run-strategy-button":
        if stored_data is None:
            return current_fig, None, "Please wait for the chart to load."
        df = pd.read_json(stored_data, orient='split')
        settings = STRATEGY_SETTINGS.get(strategy_name, {})
        strategy_class = None
        if strategy_name == "WickFillStrategy":
            strategy_class = WickFillStrategy
        if strategy_class is None:
            return current_fig, stored_data, "Selected strategy not implemented."
        performance, trade_df = backtest_strategy(
            strategy_class, df, settings,
            initial_capital=10000.0,
            fee_rate=0.001,
            slippage_rate=0.001
        )
        updated_fig = add_trade_markers(
            go.Figure(current_fig),
            trade_df.to_dict('records') if not trade_df.empty else [],
            df
        )
        updated_fig.update_layout(
            paper_bgcolor="#2c2f33",
            plot_bgcolor="#2c2f33",
            font=dict(color="white")
        )
        # Build a dark-themed table for performance metrics, narrower and aligned left/up.
        perf_table = dbc.Table(
            [
                html.Tbody([
                    html.Tr([html.Td("Total Trades"), html.Td(performance.get('total_trades', 0))]),
                    html.Tr([html.Td("Win Rate"), html.Td(f"{performance.get('win_rate', 0):.2%}")]),
                    html.Tr([html.Td("Total Net Profit"), html.Td(f"{performance.get('total_net_profit', 0):.2f}")]),
                    html.Tr([html.Td("Max Drawdown"), html.Td(f"{performance.get('max_drawdown', 0):.2%}")]),
                    html.Tr([html.Td("Sharpe Ratio"), html.Td(f"{performance.get('sharpe_ratio', 0):.2f}")]),
                    html.Tr([html.Td("Final Capital"), html.Td(f"{performance.get('final_capital', 0):.2f}")])
                ])
            ],
            bordered=True,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style={"marginTop": "5px", "marginLeft": "20px", "maxWidth": "600px"}
        )
        return updated_fig, stored_data, perf_table

    # Otherwise (on initial load or parameter change), load/update the chart.
    try:
        start_dt = datetime.datetime.fromisoformat(start_date)
        start_ms = int(start_dt.timestamp() * 1000)
    except Exception as e:
        logger.error("Error parsing start_date: %s", e)
        start_ms = None
    try:
        end_dt = datetime.datetime.fromisoformat(end_date)
    except Exception as e:
        logger.error("Error parsing end_date: %s", e)
        end_dt = None

    try:
        df = data_fetcher_instance.fetch_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            since=start_ms,
            limit=1000,
            use_cache=False
        )
    except Exception as e:
        logger.error("Error fetching historical data: %s", e)
        df = pd.DataFrame()

    logger.info("Fetched %d rows of data for %s", len(df), symbol)
    if end_dt is not None and not df.empty:
        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No data available for {symbol} in the selected date range.",
            paper_bgcolor="#2c2f33",
            plot_bgcolor="#2c2f33",
            font=dict(color="white")
        )
        return fig, None, ""
    fig = create_candlestick_figure(df, title=f"{symbol} Candlestick Chart")
    fig.update_layout(
        paper_bgcolor="#2c2f33",
        plot_bgcolor="#2c2f33",
        font=dict(color="white")
    )
    json_data = df.to_json(date_format='iso', orient='split')
    return fig, json_data, ""

if __name__ == '__main__':
    app.run_server(debug=True)
