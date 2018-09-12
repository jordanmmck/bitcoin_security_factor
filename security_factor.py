import os
import json
import requests
import datetime as dt
import calendar
import math
import pprint
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


PROJECTED_BLOCKS_LIMIT = 1200000

# get data
if not os.path.isfile('./block_data.json'):
    # get_data()
    pass

with open('block_data_modified.json') as f:
    block_data = json.load(f)


# add supply data, fee security factor, block reward security factor
supply = 0
for block in block_data:
    block['supply'] = supply
    supply += block['reward_block']

    if supply == 0:
        block['fee_sf'] = 0
        block['block_reward_sf'] = 0
    else:
        block['fee_sf'] = block['reward_fees'] / supply
        block['block_reward_sf'] = block['reward_block'] / supply


# project block rewards for future blocks
block_num = block_data[-1]['block']
block_reward = block_data[-1]['reward_block']
supply = block_data[-1]['supply'] + block_data[-1]['reward_block']

projected_rewards = []

for block_num in range(block_num+1, PROJECTED_BLOCKS_LIMIT):
    if block_num % 210000 == 0:
        block_reward /= 2
    try:
        block_reward_sf = block_reward / supply
    except ZeroDivisionError:
        block_reward_sf = 0

    projected_rewards.append({
                "block_num": block_num,
                "block_reward_sf": block_reward_sf 
            })
    supply += block_reward


# get arrays to plot
block_nums_arr = np.array([d['block'] for d in block_data])
block_reward_sf_arr = np.array([d['block_reward_sf'] for d in block_data])
fee_sf_arr = np.array([d['fee_sf'] for d in block_data])

# projected block rewards
proj_block_nums_arr = np.array([d['block_num'] for d in projected_rewards])
proj_block_rewards_arr = np.array([d['block_reward_sf'] for d in projected_rewards])

# plot known block rewards and fees
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

plt.xlabel('Block Number')
plt.ylabel('Security Factor')
plt.title('Bitcoin Security Factor Projection')
plt.legend()

plt.ylim(ymin=0, ymax=5E-6)
plt.xlim(xmin=0, xmax=1200000)
plt.show()
