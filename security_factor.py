import os
import json
import requests
import datetime
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from helper import avg


# no data until Aug. 18 2010
arguments = '?format=json&start=2010-08-18&timespan=10year'
base_url = 'https://api.blockchain.info/charts/'

if not os.path.isfile('./mcap_data.json'):
    data = requests.get(base_url + 'market-cap' + arguments).json()
    with open('mcap_data.json', 'w') as outfile:
        json.dump(data, outfile)

if not os.path.isfile('./miner_rev_data.json'):
    data = requests.get(base_url + 'miners-revenue' + arguments).json()
    with open('miner_rev_data.json', 'w') as outfile:
        json.dump(data, outfile)

if not os.path.isfile('./tx_fees_data.json'):
    data = requests.get(base_url + 'transaction-fees-usd' + arguments).json()
    with open('tx_fees_data.json', 'w') as outfile:
        json.dump(data, outfile)

with open('mcap_data.json') as f:
    mcap_data = json.load(f)['values']

with open('miner_rev_data.json') as f:
    rev_data = json.load(f)['values']

with open('tx_fees_data.json') as f:
    fee_data = json.load(f)['values']


fee_ratios = []
rev_ratios = []
days = []

lin_reg_days = []
lin_reg_fee_ratios = []

start_date = datetime.datetime.fromtimestamp(fee_data[0]['x'])
end_date = start_date + datetime.timedelta(days=365*10)
day = start_date

for mcap_dict, rev_dict, fee_dict in zip(mcap_data, rev_data, fee_data):
    mcap = mcap_dict['y']
    rev = rev_dict['y']
    fee = fee_dict['y']

    fee_ratio = fee/mcap
    rev_ratio = rev/mcap
    lin_reg_days.append(float(mcap_dict['x']))
    lin_reg_fee_ratios.append(fee_ratio)

    fee_ratios.append(fee_ratio)
    rev_ratios.append(rev_ratio)

    days.append(day)
    # data points exist for every other day only
    day += datetime.timedelta(days=2)


avg_fee_ratio = avg(fee_ratios)
avg_rev_ratio = avg(rev_ratios)

print('Average Daily Security Factor: {0:.7f}'.format(avg_rev_ratio))
print('Average Daily Fee-Only Security Factor: {0:.9f}'.format(avg_fee_ratio))


start_plot = start_date - datetime.timedelta(days=100)
end_plot = end_date - datetime.timedelta(days=500)

# Plot revenue security factor (full)
plt.ylim(ymin=0, ymax=0.0032)
plt.xlim(xmin=start_plot, xmax=end_plot)
plt.plot(days, rev_ratios, label='Daily miner revenue to market cap ratio')
plt.hlines(avg_fee_ratio, start_plot, end_date, color='red', linewidth=0.6, label='Daily fee revenue to market cap ratio (all-time average)')
plt.xlabel('Date')
plt.ylabel('Security Factor (miner revenue / market cap)')
plt.title('Bitcoin Security Factor')
plt.legend()
plt.show()

start_plot = start_date + datetime.timedelta(days=350)
end_plot = end_date - datetime.timedelta(days=600)

# Plot revenue security factor (med zoom)
plt.ylim(ymin=0, ymax=0.0008)
plt.xlim(xmin=start_plot, xmax=end_plot)
plt.plot(days, rev_ratios, label='Daily miner revenue to market cap ratio')
plt.hlines(avg_fee_ratio, start_plot, end_plot, color='red', linewidth=0.6, label='Daily fee revenue to market cap ratio (all-time average)')
plt.xlabel('Date')
plt.ylabel('Security Factor (miner revenue / market cap)')
plt.title('Bitcoin Security Factor')
plt.legend()
plt.show()

start_plot = start_date + datetime.timedelta(days=1800)
end_plot = end_date - datetime.timedelta(days=600)

# Plot revenue security factor (close zoom)
plt.ylim(ymin=0, ymax=0.0003)
plt.xlim(xmin=start_plot, xmax=end_plot)
plt.plot(days, rev_ratios, label='Daily miner revenue to market cap ratio')
plt.hlines(avg_fee_ratio, start_plot, end_plot, color='red', linewidth=0.6, label='Daily fee revenue to market cap ratio (all-time average)')
plt.xlabel('Date')
plt.ylabel('Security Factor (miner revenue / market cap)')
plt.title('Bitcoin Security Factor')
plt.legend()
plt.show()

start_plot = start_date - datetime.timedelta(days=100)
end_plot = end_date - datetime.timedelta(days=600)

# Plot fee figure
plt.plot(days, fee_ratios)
plt.ylim(ymin=0, ymax=0.00005)
plt.xlim(xmin=start_plot, xmax=end_plot)
plt.hlines(avg_fee_ratio, start_plot, end_date, color='orange', linewidth=0.6, linestyle='dashed', label='Daily fee revenue to market cap ratio (all-time average)')
plt.hlines(0.000001, start_plot, end_date, color='red', linewidth=0.6, linestyle='dashed', label='estimate baseline level')
plt.xlabel('Date')
plt.ylabel('Total daily TX fees to market cap ratio')
plt.title('Bitcoin TX Fee Security Factor')
plt.legend()
plt.show()


# Plot fee figure w/lin regression
lin_reg_days = np.array(lin_reg_days, dtype=float)
lin_reg_fee_ratios = np.array(lin_reg_fee_ratios, dtype=float)

slope, intercept, r_value, p_value, std_err = stats.linregress(lin_reg_days, lin_reg_fee_ratios)
line = slope*lin_reg_days+intercept
print(slope, intercept)
line_formula = 'y = ' + str(slope) + ' x + ' + str(intercept)
print(line_formula)

plt.plot(lin_reg_days, lin_reg_fee_ratios, 'o', markersize=2, label='tx fee sec ratio')
plt.plot(lin_reg_days, line, label='optimistic fee projection')

plt.xlabel('Date')
plt.ylabel('Total daily TX fees to market cap ratio')
plt.title('Bitcoin TX Fee Security Factor Regression')

plt.legend()
plt.show()
