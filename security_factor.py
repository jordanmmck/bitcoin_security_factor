import os
import json
import requests
import datetime as dt
import calendar
import math
import pprint

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


BLOCKS_PER_DAY = 144
SATOSHI_FACTOR = 1E8

# construct supply schedule data
reward = 50 * SATOSHI_FACTOR
supply = 0
blocks = []

for block in range(2000000):
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
            'daily_fee_ratio': None,
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


# fill-in known fee values
fee_time = 0
fee_index = 0
for block in blocks:
    if block['unix_date'] >= fee_time:
        block['daily_fee'] = fee_data[fee_index]['y'] * SATOSHI_FACTOR
        block['daily_fee_ratio'] = block['daily_fee'] / block['supply']
        fee_index += 1
        try:
            fee_time = fee_data[fee_index]['x']
        except IndexError:
            break


# interpolate remaining fee values
for i, block in enumerate(blocks):
    if block['daily_fee']:
        # get index of next known fee value
        i += 1
        try:
            while not blocks[i]['daily_fee']: i += 1
            time_diff = blocks[i]
        except IndexError:
            break

# note: change all 'date' refs to 'time'
# 1. construct simple block to reward and supply map ✓
# 2. pin known dates to blocks ✓
# 3. extrapolate missing dates ✓
# 4. pin fee to every 288th block? None the rest? ✓


blocks_arr = np.array([d['block'] for d in blocks])
fees_arr = np.array([d['daily_fee_ratio'] for d in blocks])
inflations_arr = np.array([d['daily_inflation'] for d in blocks])

# slope, intercept, r_value, p_value, std_err = stats.linregress(blocks_arr, fees_arr)

plt.ylim(ymin=1E-12, ymax=1E1)
# plt.semilogy(blocks_arr, inflations_arr)
plt.ylim(ymin=0, ymax=5E-5)
plt.xlim(xmin=0, xmax=2000000)
plt.plot(blocks_arr, inflations_arr)
plt.scatter(blocks_arr, fees_arr, s=0.5)
plt.show()

# plt.plot(blocks.keys(), inflations)
# plt.scatter(block_height, fees)
# # plt.xlim(xmin=0, xmax=600000)
# plt.ylim(ymin=1E-14, ymax=1)
# plt.ylim(ymin=0, ymax=1E-5)
# plt.xlim(xmin=0, xmax=7100000)
# plt.semilogy(blocks.keys(), inflations)

# plt.xlabel('Block Number')
# plt.ylabel('Daily Security Factor')


# # Plot fee figure w/lin regression
# lin_reg_blocks = np.array([d['block'] for d in blocks], dtype=float)
# lin_reg_fee_ratios = np.array([d['daily_fee_ratio'] for d in blocks], dtype=float)

# slope, intercept, r_value, p_value, std_err = stats.linregress(lin_reg_blocks, lin_reg_fee_ratios)
# line = slope*lin_reg_blocks+intercept
# print(slope, intercept)
# line_formula = 'y = ' + str(slope) + ' x + ' + str(intercept)
# print(line_formula)

# plt.plot(lin_reg_blocks, lin_reg_fee_ratios, 'o', markersize=2, label='tx fee sec ratio')
# plt.plot(lin_reg_blocks, line, label='optimistic fee projection')

# # plt.xlabel('Date')
# # plt.ylabel('Total daily TX fees to market cap ratio')
# # plt.title('Bitcoin TX Fee Security Factor Regression')

# plt.legend()
# plt.show()
