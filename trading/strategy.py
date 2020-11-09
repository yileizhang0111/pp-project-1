# Functions to implement our trading strategy.
import numpy as np
import trading.process as proc
import trading.indicators as indic

rng = np.random.default_rng ()


def random(stock_prices, period=7, amount=5000, fees=20, ledger='ledger_random.txt'):
    '''
    Randomly decide, every period, which stocks to purchase,
    do nothing, or sell (with equal probability).
    Spend a maximum of amount on every purchase.

    Input:
        stock_prices (ndarray): the stock price data
        period (int, default 7): how often we buy/sell (days)
        amount (float, default 5000): how much we spend on each purchase
            (must cover fees)
        fees (float, default 20): transaction fees
        ledger (str): path to the ledger file

    Output: None
    '''
    portfolio = proc.create_portfolio ([amount] * stock_prices.shape[1], stock_prices, fees, ledger)
    for i in range (period, len (stock_prices), period):
        for stock_no, share in enumerate (portfolio):
            # if share is -1, it means the company is bankruptcy
            if share == -1:
                continue
            elif stock_prices[i, stock_no] is None:
                # It defines that when element in portfolio is -1, it means never buy this company's stock.
                portfolio[stock_no] = -1
                continue
            else:
                # generate day 0 action list. 0 represent do nothing, 1 represent buy and -1 represent sell.
                if i == len (stock_prices) - 1:
                    proc.sell (i, stock_no, stock_prices, fees, portfolio, ledger_file=ledger)
                else:
                    action = np.random.randint (-1, 2, size=1)
                    if action == 1:
                        proc.buy (i, stock_no, amount, stock_prices, fees, portfolio, ledger_file=ledger)
                    elif action == -1:
                        proc.sell (i, stock_no, stock_prices, fees, portfolio, ledger_file=ledger)
    # if at the last day, it remains stock, just sell them out
    last_day = len (stock_prices) - 1
    for stock_no, share in enumerate (portfolio):
        if share > 0 and stock_prices[last_day, stock_no] is not None:
            proc.sell (last_day, stock_no, stock_prices, fees, portfolio, ledger_file=ledger)


def crossing_averages(stock_prices, fast_n=50, slow_n=200, amount=5000, fees=20, ledger='ledger_random.txt'):
    """
    Decide by crossing average method.

    Input:
        stock_prices(ndarray): stock prices
        fast_n: n of FMA
        slow_n: n of SMA
        amount: input amount
        fees: fees of transaction
        ledger: ledger file name

    Output:
        (FMA,SMA):(ndarray,ndarray) the ma indicator of this price.
    """

    FMA = np.full_like (stock_prices, fill_value= None)
    SMA = np.full_like (stock_prices, fill_value= None)
    for stock_no in range (stock_prices.shape[1]):
        FMA[fast_n - 1:, stock_no] = indic.moving_average (stock_prices[:, stock_no], fast_n)
        SMA[slow_n - 1:, stock_no] = indic.moving_average (stock_prices[:, stock_no], slow_n)
    actions_buy = np.where (FMA < SMA, 1, 0)
    actions_sell = np.where (FMA > SMA, -1, 0)
    portfolio = proc.create_portfolio ([amount] * stock_prices.shape[1], stock_prices, fees, ledger)
    for i in range (1, len (stock_prices)):
        for stock_no, share in enumerate (portfolio):
            # if share is -1, it means the company is bankruptcy
            if share == -1:
                continue
            elif stock_prices[i, stock_no] is None:
                # It defines that when element in portfolio is -1, it means never buy this company's stock.
                portfolio[stock_no] = -1
                continue
            else:
                if actions_buy[i, stock_no] == 1 and stock_prices[i, stock_no] > stock_prices[i - 1, stock_no]:
                    proc.buy (i, stock_no, amount, stock_prices, fees, portfolio, ledger)
                elif actions_sell[i, stock_no] == 1 and stock_prices[i, stock_no] < stock_prices[i - 1, stock_no]:
                    proc.sell (i, stock_no, stock_prices, fees, portfolio, ledger)
    # if at the last day, it remains stock, just sell them out
    last_day = len (stock_prices) - 1
    for stock_no, share in enumerate (portfolio):
        if share > 0 and stock_prices[last_day, stock_no] is not None:
            proc.sell (last_day, stock_no, stock_prices, fees, portfolio, ledger_file=ledger)
    return FMA, SMA


def momentum(stock_prices, period=7, low_threshold=0.3, up_threshold=0.7, amount=5000, fees=20, osc_type="stochastic",
             ledger='ledger_random.txt', cool_down_period=4):
    """
    using oscillator indicator to get portfolio.
    Input:
        stock_prices(ndarray): stock prices
        period: n of FMA
        low_threshold: the down threshold of indicator
        up_threshold: the up threshold of indicator
        amount: input amount
        osc_type: oscillator type
        fees: fees of transaction
        ledger: ledger file name
        cool_down_period: time to cool down
    Output:
        osc: osc result
    """
    osc = np.full_like (stock_prices, None)
    cool_down_table = [0]*stock_prices.shape[1]
    for stock_no in range (stock_prices.shape[1]):
        osc[period - 1:, stock_no] = indic.oscillator (stock_prices[:, stock_no], period, osc_type)
    portfolio = proc.create_portfolio ([amount] * stock_prices.shape[1], stock_prices, fees, ledger)
    for i in range (1, len (stock_prices)):
        for stock_no, share in enumerate (portfolio):
            if cool_down_table[stock_no] > 0:
                cool_down_table[stock_no] -= 1
                continue
            # if share is -1, it means the company is bankruptcy
            if share == -1:
                continue
            elif stock_prices[i, stock_no] is None or np.isnan(stock_prices[i, stock_no]) :
                # It defines that when element in portfolio is -1, it means never buy this company's stock.
                portfolio[stock_no] = -1
                continue
            else:
                if osc[i, stock_no] > up_threshold:
                    proc.buy (i, stock_no, amount, stock_prices, fees, portfolio, ledger)
                elif osc[i, stock_no] < low_threshold:
                    proc.sell (i, stock_no, stock_prices, fees, portfolio, ledger)
                cool_down_table[stock_no] = cool_down_period
    last_day = len (stock_prices) - 1
    for stock_no, share in enumerate (portfolio):
        if share > 0 and stock_prices[last_day, stock_no] is not None:
            proc.sell (last_day, stock_no, stock_prices, fees, portfolio, ledger_file=ledger)
    return osc