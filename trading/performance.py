# Evaluate performance.
import pandas as pd

def read_ledger(ledger_file):
    '''
    Reads and reports useful information from ledger_file.
    '''
    data = pd.read_csv(ledger_file,header=None)
    data.columns = ['type', 'date', 'stock', 'num_of_shares', 'price', 'total']
    transaction_num = len(data)
    total_amount_spent = abs(data[data.total < 0]['total'].sum())
    total_amount_earn = abs(data[data.total > 0]['total'].sum())
    total_profit = data['total'].sum()
    print(f"the total number of transactions performed is {transaction_num}")
    print (f"the total amount spent over 5 years {total_amount_spent}")
    print (f"the total amount earned over 5 years {total_amount_earn}")
    print (f"the overall profit or loss over 5 years {total_profit}")
    print(f"the state of your portfolio just before the last day:")
    all_in = data[data.type == 'buy'].groupby ('stock').sum ()['num_of_shares']
    all_out = data[data.type == 'sell'].groupby ('stock').sum ()['num_of_shares']
    portfolio = all_in - all_out
    for i,row in portfolio.iteritems():
        print(i,row)