import os
import requests
import json
import datetime

import matplotlib.pyplot as plt

from helper import avg


# data range: Jan. 03, 2009 - Jan. 03, 2019 (max)
mcap_data_url = 'https://api.blockchain.info/charts/market-cap?&format=json&start=2009-01-01&timespan=10year'
miner_rev_data_url = 'https://api.blockchain.info/charts/miners-revenue?&format=json&start=2009-01-01&timespan=10year'
tx_fees_data_url = 'https://api.blockchain.info/charts/transaction-fees-usd?&format=json&start=2009-01-01&timespan=10year'

# get mcap data if you don't have it
if not os.path.isfile('./mcap_data.json'):
    mcap_data = requests.get(mcap_data_url).json()
    with open('mcap_data.json', 'w') as outfile:
        json.dump(mcap_data, outfile)

# get miner revenue data if you don't have it
if not os.path.isfile('./miner_rev_data.json'):
    miner_rev_data = requests.get(miner_rev_data_url).json()
    with open('miner_rev_data.json', 'w') as outfile:
        json.dump(miner_rev_data, outfile)

# get fee data if you don't have it
if not os.path.isfile('./tx_fees_data.json'):
    tx_fees_data = requests.get(tx_fees_data_url).json()
    with open('tx_fees_data.json', 'w') as outfile:
        json.dump(tx_fees_data, outfile)

with open('mcap_data.json') as f:
    mcap_data = json.load(f)['values']

with open('miner_rev_data.json') as f:
    rev_data = json.load(f)['values']

with open('tx_fees_data.json') as f:
    fee_data = json.load(f)['values']

fee_ratios = []
ratios = []
days = []

# Jan. 03, 2009 GMT
day = datetime.datetime.fromtimestamp(fee_data[0]['x'])

for mcap_dict, rev_dict, fee_dict in zip(mcap_data, rev_data, fee_data):
    mcap = float(mcap_dict['y'])
    rev = float(rev_dict['y'])
    fee = float(fee_dict['y'])

    try:
        fee_ratio = fee/mcap
    except ZeroDivisionError as e:
        fee_ratio = None

    fee_ratios.append(fee_ratio)

    try:
        ratio = rev/mcap
    except ZeroDivisionError as e:
        ratio = None

    ratios.append(ratio)

    days.append(day)
    # dataset covers every other day only
    day += datetime.timedelta(days=2)

print('Avgerage Daily Security Factor: {0:.7f}%'.format(avg(ratios)*100))
print('Avgerage Daily Fee Security Factor: {0:.7f}%'.format(avg(fee_ratios)*100))

# Plot rev figure
plt.plot(days, ratios)
plt.xlabel('Date')
plt.ylabel('Total daily miner revenue to market cap ratio')
plt.title('Bitcoin Security Factor')
plt.show()

# Plot fee figure
plt.plot(days, fee_ratios)
plt.xlabel('Date')
plt.ylabel('Total daily TX fees to market cap ratio')
plt.title('Bitcoin TX Fee Security Factor')
plt.show()
