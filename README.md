# Backtesting Tool for Trading Strategies

A modular backtesting tool built with Python for simulating and analyzing trading strategies using historical data.

## Motivations

This project stems from a desire to rigorously test trading hypotheses in a structured, data-driven way.

For example:  
> "When Asset X is trading within a defined range, any wick (upward or downward) in a given timeframe is likely to be filled within a set period — making it a potentially profitable entry."

The goal is to build a tool flexible enough to:
- Formulate hypotheses like this,
- Backtest them under various market conditions,
- Evaluate performance using statistical measures.

I’m working under the assumption that fully automated, always-on profitable trading bots are rare — if they exist at all. A more realistic approach is to:
- Identify conditions where a strategy performs well,
- Deploy it only when those conditions are present,
- Continuously monitor and disable it when the market shifts.

This tool is intended to support that kind of hypothesis-driven, adaptable trading workflow.

## Features

- Load and preprocess historical price data
- Define and plug in custom trading strategies
- Visualize strategy performance with plots
- Track key metrics like win/loss ratio and returns

## Tech Stack

- Python
- Matplotlib / Plotly
- Pytest
- Custom modular architecture

## Getting Started

### Installation
pip install -r requirements.txt

### Usage
python app.py

Modify `strategies.py` to define your own logic or use examples provided in `strategy_settings.py`.

## Testing
pytest

## Project Structure

- app.py — Entry point
- backtester.py — Core backtesting engine
- strategies.py — Custom strategy definitions
- plot_utils.py — Visualization utilities
- data_fetcher.py — Market data handling

## Author

Thomas Haile — GitHub: @thomasih
