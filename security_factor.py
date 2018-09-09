import os
import json
import requests
import datetime as dt
import calendar
import math
import pprint

import matplotlib.pyplot as plt
import numpy as np


# construct supply schedule data
BLOCKS_PER_DAY = 144
# use satoshis
reward = 5000000000
supply = 0
blocks = []

for block in range(7000000):
    try:
        daily_inflation = reward * BLOCKS_PER_DAY / supply
    except ZeroDivisionError:
        daily_inflation = math.inf
    blocks.append({
            'block': block, 
            'supply': supply, 
            'block_reward': reward,
            'daily_inflation': daily_inflation,
            'daily_fee': None,
            'date': None,
            'unix_date': None
        })
    if block % 210000 == 0 and block > 0:
        reward = reward//2
    supply += reward

# block discovery dates
# https://en.bitcoin.it/wiki/Controlled_supply
# https://www.blockchain.com/btc/block-height/540000
block_dates = {
    0: {'date': '2009-01-03', 'unix_date': None, 'time_step': None},
    52500: {'date': '2010-04-22', 'unix_date': None, 'time_step': None},
    105000: {'date': '2011-01-28', 'unix_date': None, 'time_step': None},
    157500: {'date': '2011-12-14', 'unix_date': None, 'time_step': None},
    210000: {'date': '2012-11-28', 'unix_date': None, 'time_step': None},
    262500: {'date': '2013-10-09', 'unix_date': None, 'time_step': None},
    315000: {'date': '2014-08-11', 'unix_date': None, 'time_step': None},
    367500: {'date': '2015-07-29', 'unix_date': None, 'time_step': None},
    420000: {'date': '2016-07-09', 'unix_date': None, 'time_step': None},
    472500: {'date': '2017-06-23', 'unix_date': None, 'time_step': None},
    525000: {'date': '2018-05-29', 'unix_date': None, 'time_step': None},
    540000: {'date': '2018-09-05', 'unix_date': None, 'time_step': None},
}

# add unix times
block_list = sorted(block_dates.keys())
for block in block_list:
    block_dates[block]['unix_date'] = calendar.timegm(
            dt.datetime.strptime(block_dates[block]['date'], '%Y-%m-%d').timetuple()
        )

# interpolate missing block times
for i, block in enumerate(block_list):
    try:
        time_diff = block_dates[block_list[i+1]]['unix_date'] - block_dates[block]['unix_date']
        block_diff = block_list[i+1] - block
        block_dates[block]['time_step'] = time_diff/block_diff
    except IndexError:
        block_dates[block]['time_step'] = 10*60

# add interpolated time into blocks data
curr_time_step = None
prev_ref_time = None
prev_ref_block = None
for block in blocks:
    block_num = block['block']
    try:
        curr_time_step = block_dates[block_num]['time_step']
        prev_ref_time = block_dates[block_num]['unix_date']
        prev_ref_block = block_num
    except KeyError:
        pass
    unix_date = math.floor(
            prev_ref_time + ((block_num - prev_ref_block) * curr_time_step)
        )
    block['unix_date'] = unix_date
    block['date'] = dt.datetime.utcfromtimestamp(unix_date)

# get fee data
arguments = '?format=json&start=2009-01-01&timespan=10year'
base_url = 'https://api.blockchain.info/charts/'
if not os.path.isfile('./tx_fees_data.json'):
    data = requests.get(base_url + 'transaction-fees' + arguments).json()
    with open('tx_fees_data.json', 'w') as outfile:
        json.dump(data, outfile)

with open('tx_fees_data.json') as f:
    fee_data = json.load(f)['values']


# fill-in and interpolate fees
fee_index = 0
fee_step = 0
prev_fee = fee_data[0]['y']
next_fee = 0
prev_fee_time = fee_data[0]['x']
next_fee_time = None
for block in blocks:
    if block['unix_date'] >= prev_fee_time:
        try:
            prev_fee_time = fee_data[fee_index]['x']
            prev_fee = fee_data[fee_index]['y']

            next_fee_time = fee_data[fee_index+1]['x']
            next_fee = fee_data[fee_index+1]['y']

            fee_diff = next_fee - prev_fee
            time_diff = next_fee_time - prev_fee_time
            fee_step = fee_diff / time_diff

            fee_index += 1
        except IndexError:
            break
    block['daily_fee'] = prev_fee + ((block['unix_date'] - prev_fee_time) * fee_step)
    try:
        block['daily_fee'] /= block['supply']
    except ZeroDivisionError:
        pass


# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(blocks[530000:530005])
# pp.pprint(fee_data[0:2])

# blocks
# [   {   'block': 0,
#         'block_reward': 5000000000,
#         'daily_fee': None,
#         'daily_inflation': inf,
#         'date': datetime.datetime(2009, 1, 3, 0, 0),
#         'supply': 0,
#         'unix_date': 1230940800},
#     {   'block': 1,
#         'block_reward': 5000000000,
#         'daily_fee': None,
#         'daily_inflation': 144.0,
#         'date': datetime.datetime(2009, 1, 3, 0, 13),
#         'supply': 5000000000,
#         'unix_date': 1230941580}
# ]

# fee_data
# [
#     {'x': 1230940800, 'y': 0.0}, 
#     {'x': 1231113600, 'y': 0.0}
# ]

# note: change all 'date' refs to 'time'
# 1. construct simple block to reward and supply map ✓
# 2. pin known dates to blocks ✓
# 3. extrapolate missing dates ✓
# 4. pin fee to every 288th block? None the rest? ✓



# (BTC issued)/(total supply) as a function of day and/or block height.
# (BTC paid in fees)/(total supply) 
# (BTC issued + BTC paid in fees)/(total supply) 

block_height = np.array([d['block'] for d in blocks])
inflations = np.array([d['daily_inflation'] for d in blocks])
fees = np.array([d['daily_fee'] for d in blocks])
plt.semilogy(block_height, inflations)
plt.semilogy(block_height, fees)
plt.show()

# plt.plot(blocks.keys(), inflations)
# plt.ylim(ymin=1E-14, ymax=1)
# plt.ylim(ymin=0, ymax=1E-5)
# plt.xlim(xmin=0, xmax=7100000)
# plt.semilogy(blocks.keys(), inflations)

# plt.xlabel('Block Number')
# plt.ylabel('Daily Security Factor')
