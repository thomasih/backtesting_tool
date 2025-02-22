# strategies.py
import pandas as pd
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    
    Each strategy must implement the run() method and populate the 'trades' list.
    """
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.trades = []  # List of trade dictionaries

    @abstractmethod
    def run(self) -> list:
        """
        Execute the strategy logic and return a list of trades.
        """
        pass

class WickFillStrategy(Strategy):
    """
    Implements a Wick Fill trading strategy.
    """
    def __init__(self, data: pd.DataFrame, wick_threshold: float = 0.5, range_window: int = 20, 
                 range_factor: float = 1.5, risk_reward_ratio: float = 2.0, stop_buffer: float = 0.005,
                 max_holding_period: int = 10) -> None:
        super().__init__(data)
        self.wick_threshold = wick_threshold
        self.range_window = range_window
        self.range_factor = range_factor
        self.risk_reward_ratio = risk_reward_ratio
        self.stop_buffer = stop_buffer
        self.max_holding_period = max_holding_period

    def is_range_bound(self, idx: int) -> bool:
        """
        Check if the market is range-bound based on the previous candles.
        """
        if idx < self.range_window:
            return False
        window = self.data.iloc[idx - self.range_window: idx]
        overall_range = window['High'].max() - window['Low'].min()
        avg_range = (window['High'] - window['Low']).mean()
        return overall_range < self.range_factor * avg_range

    def run(self) -> list:
        """
        Run the WickFill strategy and generate trades.
        """
        self.trades = []
        i = self.range_window  # start once we have enough candles
        data = self.data
        while i < len(data) - 1:
            candle = data.iloc[i]
            open_price = candle['Open']
            close_price = candle['Close']
            high_price = candle['High']
            low_price = candle['Low']
            body = abs(close_price - open_price)
            if body == 0:
                i += 1
                continue

            trade_triggered = False
            if not self.is_range_bound(i):
                i += 1
                continue

            # Long trade signal: if upper wick is unusually long.
            if (high_price - max(open_price, close_price)) / body >= self.wick_threshold:
                if i + 1 < len(data):
                    entry_candle = data.iloc[i+1]
                    entry_time = data.index[i+1]
                    entry_price = entry_candle['Open']
                    stop_loss = low_price * (1 - self.stop_buffer)
                    risk = entry_price - stop_loss
                    take_profit = entry_price + self.risk_reward_ratio * risk
                    exit_found = False
                    for j in range(i+1, min(i+1+self.max_holding_period, len(data))):
                        current_candle = data.iloc[j]
                        if current_candle['Low'] <= stop_loss:
                            exit_time = data.index[j]
                            exit_price = stop_loss
                            exit_found = True
                            break
                        elif current_candle['High'] >= take_profit:
                            exit_time = data.index[j]
                            exit_price = take_profit
                            exit_found = True
                            break
                    if not exit_found:
                        exit_time = data.index[i+1+self.max_holding_period-1]
                        exit_price = data.iloc[i+1+self.max_holding_period-1]['Close']
                    self.trades.append({
                        'trade_type': 'long',
                        'entry_time': entry_time,
                        'entry_price': entry_price,
                        'exit_time': exit_time,
                        'exit_price': exit_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                    })
                    trade_triggered = True

            # Short trade signal: if lower wick is unusually long.
            if (min(open_price, close_price) - low_price) / body >= self.wick_threshold and not trade_triggered:
                if i + 1 < len(data):
                    entry_candle = data.iloc[i+1]
                    entry_time = data.index[i+1]
                    entry_price = entry_candle['Open']
                    stop_loss = high_price * (1 + self.stop_buffer)
                    risk = stop_loss - entry_price
                    take_profit = entry_price - self.risk_reward_ratio * risk
                    exit_found = False
                    for j in range(i+1, min(i+1+self.max_holding_period, len(data))):
                        current_candle = data.iloc[j]
                        if current_candle['High'] >= stop_loss:
                            exit_time = data.index[j]
                            exit_price = stop_loss
                            exit_found = True
                            break
                        elif current_candle['Low'] <= take_profit:
                            exit_time = data.index[j]
                            exit_price = take_profit
                            exit_found = True
                            break
                    if not exit_found:
                        exit_time = data.index[i+1+self.max_holding_period-1]
                        exit_price = data.iloc[i+1+self.max_holding_period-1]['Close']
                    self.trades.append({
                        'trade_type': 'short',
                        'entry_time': entry_time,
                        'entry_price': entry_price,
                        'exit_time': exit_time,
                        'exit_price': exit_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                    })
                    trade_triggered = True

            # Jump ahead after a trade.
            if trade_triggered:
                try:
                    exit_idx = data.index.get_loc(exit_time)
                except Exception:
                    exit_idx = i + self.max_holding_period
                i = exit_idx + 1
            else:
                i += 1

        return self.trades
