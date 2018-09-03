import os
import requests
import json
import datetime

import matplotlib.pyplot as plt


# data range: Jan. 03, 2009 - Jan. 03, 2019 (max)
tx_fees_data_url = 'https://api.blockchain.info/charts/transaction-fees-usd?&format=json&start=2009-01-01&timespan=10year'
mcap_data_url = 'https://api.blockchain.info/charts/market-cap?&format=json&start=2009-01-01&timespan=10year'

# get fee data if you don't have it
if not os.path.isfile('./tx_fees_data.json'):
    tx_fees_data = requests.get(tx_fees_data_url).json()
    with open('tx_fees_data.json', 'w') as outfile:
        json.dump(tx_fees_data, outfile)

# get mcap data if you don't have it
if not os.path.isfile('./mcap_data.json'):
    mcap_data = requests.get(mcap_data_url).json()
    with open('mcap_data.json', 'w') as outfile:
        json.dump(mcap_data, outfile)

with open('tx_fees_data.json') as f:
    tx_data = json.load(f)['values']

with open('mcap_data.json') as f:
    mcap_data = json.load(f)['values']

ratios = []
days = []

# Jan. 03, 2009 GMT
start_timestamp = tx_data[0]['x']
day = datetime.datetime.fromtimestamp(timestamp)

for fee_dict, mcap_dict in zip(tx_data, mcap_data):
    fee = float(fee_dict['y'])
    mcap = float(mcap_dict['y'])
    try:
        ratio = fee/mcap
    except ZeroDivisionError as e:
        ratio = None
    ratios.append(ratio)
    days.append(day)
    # dataset covers every odd day only
    day += datetime.timedelta(days=2)

# Print average
sum = 0
count = 0
for r in ratios:
    if r is None:
        continue
    sum += r
    count += 1

print('Avgerage Daily Security Factor: {0:.7f}%'.format(sum/count*100))

# Plot figure
plt.plot(days, ratios)
plt.xlabel('Date')
plt.ylabel('Total daily TX fees to market cap ratio')
plt.title('Bitcoin TX Fee Security Factor')
plt.show()
