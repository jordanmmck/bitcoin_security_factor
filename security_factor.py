import os
import json
import requests
import datetime as dt
import sys

import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
from scipy import stats

from helper import avg


SECONDS_PER_YEAR = 31557600
EPOCH_2010 = 1262304000

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
unix_days = []

unix_start_time = fee_data[0]['x']
start_date = dt.datetime.fromtimestamp(unix_start_time)

end_date = start_date + dt.timedelta(days=365*10)
unix_end_time = unix_start_time + 10*SECONDS_PER_YEAR

day = start_date

for mcap_dict, rev_dict, fee_dict in zip(mcap_data, rev_data, fee_data):
    mcap = mcap_dict['y']
    rev = rev_dict['y']
    fee = fee_dict['y']

    fee_ratio = fee/mcap
    rev_ratio = rev/mcap

    fee_ratios.append(fee_ratio)
    rev_ratios.append(rev_ratio)

    unix_days.append(float(mcap_dict['x']))
    days.append(day)
    # data points exist for every other day only
    day += dt.timedelta(days=2)


avg_fee_ratio = avg(fee_ratios)
avg_rev_ratio = avg(rev_ratios)

print('Average Daily Security Factor: {0:.7f}'.format(avg_rev_ratio))
print('Average Daily Fee-Only Security Factor: {0:.9f}'.format(avg_fee_ratio))


start_plot = start_date - dt.timedelta(days=100)
end_plot = end_date - dt.timedelta(days=500)

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

start_plot = start_date + dt.timedelta(days=350)
end_plot = end_date - dt.timedelta(days=600)

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

start_plot = start_date + dt.timedelta(days=1800)
end_plot = end_date - dt.timedelta(days=600)

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

# tx fee security factor
unix_days = np.array(unix_days, dtype=float)

# trendline
slope = 7.9E-15
y_intercept = -1E-5
trendline_label = 'Trendline (y = {} * UNIX_TIME + {})'.format(slope, y_intercept)
trendline = slope * unix_days + y_intercept

plt.plot(unix_days, fee_ratios, 'o', markersize=2, label='Security Factor', color='grey')
plt.plot(unix_days, trendline, label=trendline_label, color='blue', linestyle='dashed', linewidth=0.8)
plt.hlines(avg_fee_ratio, unix_start_time, unix_end_time, color='orange', linewidth=0.6, linestyle='dashed', label='Fee security factor average ({:.7f})'.format(avg_fee_ratio))

# human readable labels
unix_years = [EPOCH_2010 + SECONDS_PER_YEAR*i for i in range(1,10)]
year_labels = ['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
plt.xticks(unix_years, year_labels)

plt.ylim(ymin=-0.000001, ymax=0.00005)
plt.xlim(xmin=unix_start_time-10000000, xmax=unix_end_time-SECONDS_PER_YEAR)

plt.xlabel('Year')
plt.ylabel('Daily TX fee security factor')
plt.title('Bitcoin TX Fee Security Factor')
plt.legend()

plt.show()
