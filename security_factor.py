import os
import json
import requests
import datetime as dt
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

SECONDS_PER_YEAR = 31557600
EPOCH_2010 = 1262304000

arguments = '?format=json&start=2009-01-01&timespan=10year'
base_url = 'https://api.blockchain.info/charts/'

if not os.path.isfile('./tx_fees_data.json'):
    data = requests.get(base_url + 'transaction-fees' + arguments).json()
    with open('tx_fees_data.json', 'w') as outfile:
        json.dump(data, outfile)

with open('tx_fees_data.json') as f:
    fee_data = json.load(f)['values']

# using satoshis
BLOCKS_PER_DAY = 144
reward = 5000000000
supply = 0
blocks = {}

for block in range(0,7000000):
    try:
        daily_inflation = reward * BLOCKS_PER_DAY / supply
    except ZeroDivisionError:
        daily_inflation = math.inf
    blocks[block] = {
            'block': block, 
            'supply': supply, 
            'block_reward': reward,
            'daily_inflation': daily_inflation
        }
    if block % 210000 == 0 and block > 0:
        reward = reward//2
    supply += reward

print(blocks[0])
print(blocks[540580])

# 1. construct simple block to reward and supply map
# 2. pin known dates to blocks
# 3. extrapolate missing dates
# 4. pin fee to every 288th block? None the rest?

inflations = np.array([d['daily_inflation'] for d in blocks.values()])
plt.semilogy(blocks.keys(), inflations)
plt.show()
