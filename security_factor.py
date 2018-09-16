import os
import sys
import json
import requests
import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from get_block_data import get_data, update_data


PROJECTED_BLOCKS_LIMIT = 1500000
BLOCKS_PER_YEAR = 144 * 365

if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.isfile('data/block_data.json'):
    get_data()
else:
    update_data()

with open('data/block_data.json') as f:
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


# block reward and fees sf arrays
block_nums_arr = np.array([d['block'] for d in block_data])
block_reward_sf_arr = np.array([d['block_reward_sf'] for d in block_data])
fee_sf_arr = np.array([d['fee_sf'] for d in block_data])

# projected block rewards arrays
proj_block_nums_arr = np.array([d['block_num'] for d in projected_rewards])
proj_block_rewards_arr = np.array([d['block_reward_sf'] for d in projected_rewards])

# plot block rewards and fees
plt.plot(block_nums_arr, block_reward_sf_arr, color='#2a51fc', linewidth=2, label='block reward')
plt.plot(block_nums_arr, fee_sf_arr, color='#a5a5a5', linewidth=0.2, label='tx fee')

# plot projected block rewards
plt.plot(proj_block_nums_arr, proj_block_rewards_arr, color='#afbeff', linewidth=2, label='projected block reward')

# linear regression line
slope, intercept, _, _, _ = stats.linregress(block_nums_arr, fee_sf_arr)
all_blocks_arr = np.append(block_nums_arr, proj_block_nums_arr)
full_line = slope * all_blocks_arr + intercept

# plot regression line
plt.plot(all_blocks_arr, full_line, color='red', label='tx fee linear regression')

projected_line = slope * proj_block_nums_arr + intercept
plt.plot(proj_block_nums_arr, proj_block_rewards_arr+projected_line, color='#ddc9ff', ls='dotted', label='projected block reward + tx fee')

plt.rcParams['agg.path.chunksize'] = 100000

# assign dates to each block tick
block_dates = {
        0: 'Jan. 2009', 
        200000: 'Sept. 2012', 
        400000: 'Feb. 2016',
        600000: 'Oct. 2019',
        800000: 'Aug. 2023',
        1000000: 'May. 2027',
        1200000: 'March. 2031',
        1400000: 'Dec. 2034',
}
ax = plt.gca()
ax.set_xticklabels(list(block_dates.values()))

plt.xlabel('Date')
plt.ylabel('Security Factor (annualized)')
plt.title('Bitcoin Annualized Security Factor Projection')
plt.legend()

plt.ylim(ymin=0, ymax=.14)
plt.xlim(xmin=0, xmax=PROJECTED_BLOCKS_LIMIT)

fig = plt.gcf()
fig.set_size_inches(14.5, 8.5)
fig.savefig('figures/security_factor.png', dpi=100, bbox_inches='tight')
