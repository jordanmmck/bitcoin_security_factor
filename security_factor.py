import os
import sys
import json
import requests
import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from get_block_data import get_data


PROJECTED_BLOCKS_LIMIT = 1200000
BLOCKS_PER_YEAR = 144 * 365

# get data
if not os.path.isfile('./block_data.json'):
    get_data()

with open('block_data.json') as f:
    block_data = json.load(f)

# add supply data, fee security factor, block reward security factor
supply = 0
for block in block_data:
    block['supply'] = supply
    supply += block['block_reward']
    block['datetime'] = dt.datetime.fromtimestamp(block['timestamp'])

    if supply == 0:
        block['fee_sf'] = 0
        block['block_reward_sf'] = 0
    else:
        block['fee_sf'] = block['fees'] * BLOCKS_PER_YEAR / supply
        block['block_reward_sf'] = block['block_reward'] * BLOCKS_PER_YEAR / supply

# project block rewards for future blocks
block_num = block_data[-1]['block']
block_reward = block_data[-1]['block_reward']
supply = block_data[-1]['supply'] + block_data[-1]['block_reward']

projected_rewards = []

for block_num in range(block_num+1, PROJECTED_BLOCKS_LIMIT):
    if block_num % 210000 == 0:
        block_reward /= 2
    try:
        block_reward_sf = block_reward * BLOCKS_PER_YEAR / supply
    except ZeroDivisionError:
        block_reward_sf = 0

    projected_rewards.append({
                "block_num": block_num,
                "block_reward_sf": block_reward_sf 
            })
    supply += block_reward

# block reward and fees arrays
block_nums_arr = np.array([d['block'] for d in block_data])
block_reward_sf_arr = np.array([d['block_reward_sf'] for d in block_data])
fee_sf_arr = np.array([d['fee_sf'] for d in block_data])

# projected block rewards arrays
proj_block_nums_arr = np.array([d['block_num'] for d in projected_rewards])
proj_block_rewards_arr = np.array([d['block_reward_sf'] for d in projected_rewards])

# plot block rewards and fees
plt.plot(block_nums_arr, block_reward_sf_arr, color='#2a51fc', linewidth=2, label='block reward security factor')
plt.plot(block_nums_arr, fee_sf_arr, color='#a5a5a5', linewidth=0.2, label='fee security factor')

# plot projected block rewards
plt.plot(proj_block_nums_arr, proj_block_rewards_arr, color='#afbeff', linewidth=2, label='projected block rewards')

# linear regression line
slope, intercept, _, _, _ = stats.linregress(block_nums_arr, fee_sf_arr)
all_blocks_arr = np.append(block_nums_arr, proj_block_nums_arr)
full_line = slope * all_blocks_arr + intercept

# plot regression line
plt.plot(all_blocks_arr, full_line, color='red', label='fee security factor linear regression')

projected_line = slope * proj_block_nums_arr + intercept
plt.plot(proj_block_nums_arr, proj_block_rewards_arr+projected_line, color='#ddc9ff', ls='dotted', label='block rewards + tx fees security factor')

plt.rcParams['agg.path.chunksize'] = 100000

plt.xlabel('Block Number')
plt.ylabel('Annualized Security Factor')
plt.title('Bitcoin Annualized Security Factor Projection')
plt.legend()

plt.ylim(ymin=0, ymax=.14)
plt.xlim(xmin=0, xmax=1200000)

fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)
fig.savefig('security_factor.png', dpi=100)
