import os
import json
import requests
import datetime as dt
import time
import calendar
import sys
import math

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
for block in range(0,700000):
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

# 1. construct simple block to reward and supply map
# 2. pin known dates to blocks
# 3. extrapolate missing dates
# 4. pin fee to every 288th block? None the rest?

# block discovery dates
# source: https://en.bitcoin.it/wiki/Controlled_supply
block_dates = {
    0: '2009-01-03',
    52500: '2010-04-22',
    105000: '2011-01-28',
    157500: '2011-12-14',
    210000: '2012-11-28',
    262500: '2013-10-09',
    315000: '2014-08-11',
    367500: '2015-07-29',
    420000: '2016-07-09',
    472500: '2017-06-23',
    525000: '2018-05-29'
}

# add unix times
for block in block_dates:
    block_date = block_dates[block]
    blocks[block]['date'] = block_date
    blocks[block]['unix_date'] = calendar.timegm(
            dt.datetime.strptime(block_date, '%Y-%m-%d').timetuple()
        )


# inflations = np.array([d['daily_inflation'] for d in blocks.values()])
# plt.semilogy(blocks.keys(), inflations)
# plt.ylim(ymin=1E-14, ymax=1)
# plt.xlabel('Block Number')
# plt.ylabel('Daily Security Factor')
# plt.show()
