# plot_utils.py
import plotly.graph_objs as go

def create_candlestick_figure(df, title="Candlestick Chart"):
    """
    Create and return a Plotly candlestick chart with dark-themed layout.
    """
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price Data"
    )])
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#2c2f33",
        plot_bgcolor="#2c2f33",
        font=dict(color="white")
    )
    return fig

def add_trade_markers(fig, trades, data):
    """
    Overlay trade markers on the given chart using contrasting colors.
    """
    long_entry_x, long_entry_y = [], []
    long_exit_x, long_exit_y = [], []
    short_entry_x, short_entry_y = [], []
    short_exit_x, short_exit_y = [], []
    
    for trade in trades:
        trade_type = trade.get('trade_type')
        if trade_type == 'long':
            long_entry_x.append(trade.get('entry_time'))
            long_entry_y.append(trade.get('entry_price'))
            long_exit_x.append(trade.get('exit_time'))
            long_exit_y.append(trade.get('exit_price'))
        elif trade_type == 'short':
            short_entry_x.append(trade.get('entry_time'))
            short_entry_y.append(trade.get('entry_price'))
            short_exit_x.append(trade.get('exit_time'))
            short_exit_y.append(trade.get('exit_price'))
    
    if long_entry_x:
        fig.add_trace(go.Scatter(
            x=long_entry_x,
            y=long_entry_y,
            mode='markers',
            marker=dict(color='cyan', symbol='triangle-up', size=12),
            name='Long Entry'
        ))
    if long_exit_x:
        fig.add_trace(go.Scatter(
            x=long_exit_x,
            y=long_exit_y,
            mode='markers',
            marker=dict(color='magenta', symbol='triangle-down', size=12),
            name='Long Exit'
        ))
    if short_entry_x:
        fig.add_trace(go.Scatter(
            x=short_entry_x,
            y=short_entry_y,
            mode='markers',
            marker=dict(color='orange', symbol='square', size=12),
            name='Short Entry'
        ))
    if short_exit_x:
        fig.add_trace(go.Scatter(
            x=short_exit_x,
            y=short_exit_y,
            mode='markers',
            marker=dict(color='dodgerblue', symbol='diamond', size=12),
            name='Short Exit'
        ))
    
    return fig
