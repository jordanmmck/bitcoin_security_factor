import os
import json
import requests
import datetime as dt
import time
import calendar
import sys
import math
import pprint

import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
from scipy import stats

from helper import avg


# (BTC issued)/(total supply) as a function of day and/or block height.
# (BTC paid in fees)/(total supply) 
# (BTC issued + BTC paid in fees)/(total supply) 

arguments = '?format=json&start=2009-01-01&timespan=10year'
base_url = 'https://api.blockchain.info/charts/'

if not os.path.isfile('./tx_fees_data.json'):
    data = requests.get(base_url + 'transaction-fees' + arguments).json()
    with open('tx_fees_data.json', 'w') as outfile:
        json.dump(data, outfile)

with open('tx_fees_data.json') as f:
    fee_data = json.load(f)['values']


# use satoshis
BLOCKS_PER_DAY = 144
reward = 5000000000
supply = 0
blocks = {}

# construct supply schedule
for block in range(0,7000000):
    try:
        daily_inflation = reward * BLOCKS_PER_DAY / supply
    except ZeroDivisionError:
        daily_inflation = math.inf
    blocks[block] = {
            'block': block, 
            'supply': supply, 
            'block_reward': reward,
            'daily_inflation': daily_inflation,
            'date': None,
            'unix_date': None
        }
    if block % 210000 == 0 and block > 0:
        reward = reward//2
    supply += reward

# block discovery dates
# https://en.bitcoin.it/wiki/Controlled_supply
# https://www.blockchain.com/btc/block-height/540000
block_dates = [
    {'block': 0, 'date': '2009-01-03', 'unix_date': None, 'time_step': None},
    {'block': 52500, 'date': '2010-04-22', 'unix_date': None, 'time_step': None},
    {'block': 105000, 'date': '2011-01-28', 'unix_date': None, 'time_step': None},
    {'block': 157500, 'date': '2011-12-14', 'unix_date': None, 'time_step': None},
    {'block': 210000, 'date': '2012-11-28', 'unix_date': None, 'time_step': None},
    {'block': 262500, 'date': '2013-10-09', 'unix_date': None, 'time_step': None},
    {'block': 315000, 'date': '2014-08-11', 'unix_date': None, 'time_step': None},
    {'block': 367500, 'date': '2015-07-29', 'unix_date': None, 'time_step': None},
    {'block': 420000, 'date': '2016-07-09', 'unix_date': None, 'time_step': None},
    {'block': 472500, 'date': '2017-06-23', 'unix_date': None, 'time_step': None},
    {'block': 525000, 'date': '2018-05-29', 'unix_date': None, 'time_step': None},
    {'block': 540000, 'date': '2018-09-05', 'unix_date': None, 'time_step': None},
]

# add unix times
for block in block_dates:
    block_date = block['date']
    block['unix_date'] = calendar.timegm(
            dt.datetime.strptime(block_date, '%Y-%m-%d').timetuple()
        )

# interpolate missing block times
for i, block in enumerate(block_dates):
    try:
        time_diff = block_dates[i+1]['unix_date'] - block['unix_date']
        block_diff = block_dates[i+1]['block'] - block['block']
        block['time_step'] = time_diff/block_diff
    except IndexError:
        block['time_step'] = 10*60

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(block_dates)

# 1. construct simple block to reward and supply map
# 2. pin known dates to blocks
# 3. extrapolate missing dates
# 4. pin fee to every 288th block? None the rest?

inflations = np.array([d['daily_inflation'] for d in blocks.values()])
# dates = np.array([d['date'] for d in blocks.values()])
# dates = np.array([d['date'] for d in blocks.values()])
plt.semilogy(blocks.keys(), inflations)
# plt.plot(blocks.keys(), inflations)
# plt.ylim(ymin=1E-14, ymax=1)
# plt.ylim(ymin=0, ymax=1E-5)
plt.xlim(xmin=0, xmax=7100000)
# plt.xlabel('Block Number')
# plt.ylabel('Daily Security Factor')
plt.show()
