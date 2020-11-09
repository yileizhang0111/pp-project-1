import numpy as np


def moving_average(stock_price, n=7, weights=[]):
    '''
    Calculates the n-day (possibly weighted) moving average for a given stock over time.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        weights (list, default []): must be of length n if specified. Indicates the weights
            to use for the weighted average. If empty, return a non-weighted average.

    Output:
        ma (ndarray): the n-day (possibly weighted) moving average of the share price over time.
    '''
    # Lines X-Y: gordoncluster
    # URL: https://gordoncluster.wordpress.com/2014/02/13/python-numpy-how-to-generate-moving-averages-efficiently-part-2/
    # Python numpy How to Generate Moving Averages Efficiently Part 2, 2014
    # Accessed on 7 Nov 2020.
    if len (weights) == 0:
        weights = np.repeat (1.0, n) / n
    ma = np.convolve (stock_price, weights, 'valid')
    return ma


def oscillator(stock_price, n=7, osc_type='stochastic'):
    '''
    Calculates the level of the stochastic or RSI oscillator with a period of n days.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.

    Output:
        osc (ndarray): the oscillator level with period $n$ for the stock over time.
    '''
    start = 0
    end = start + n
    osc = np.zeros (len (stock_price) - n + 1)
    while end <= len (stock_price):
        if osc_type == "stochastic":
            highest = max (stock_price[start:end])
            lowest = min (stock_price[start:end])
            if highest != lowest:
                osc[start] = (stock_price[end - 1] - lowest) / (highest - lowest)
            else:
                osc[start] = 0
        elif osc_type == "RSI":
            diff = np.diff (stock_price[start:end])
            positive = np.average (diff[diff > 0]) if not np.isnan (np.average (diff[diff > 0])) else 0
            negative = abs (np.average (diff[diff < 0])) if not np.isnan (abs (np.average (diff[diff < 0]))) else 0
            if positive == 0 and negative == 0:
                osc[start] = 0
            else:
                osc[start] = positive / (negative + positive)
        start += 1
        end += 1
    return osc
