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


PROJECTED_BLOCKS_LIMIT = 1000000

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
    supply += block['block_reward']

    if supply == 0:
        block['fee_sf'] = 0
        block['block_reward_sf'] = 0
    else:
        block['fee_sf'] = block['fees'] / supply
        block['block_reward_sf'] = block['block_reward'] / supply


# project block rewards for future blocks
block_num = block_data[-1]['block']
block_reward = block_data[-1]['block_reward']
supply = block_data[-1]['supply'] + block_data[-1]['block_reward']

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

# linear regression line
slope, intercept, _, _, _ = stats.linregress(blocks_arr, fee_sf_arr)
line = slope * blocks_arr + intercept

# plot known block rewards and fees
plt.plot(blocks_arr, block_rewards_arr)
plt.plot(blocks_arr, fee_rewards_arr, color='grey', linewidth=0.2)

# plot projected block rewards
plt.plot(proj_block_nums_arr, proj_block_rewards_arr, color='grey')

# plot regression line
plt.plot(np.append(block_nums_arr, proj_block_nums_arr), line, color='red')

plt.ylim(ymin=0, ymax=5E-6)
plt.xlim(xmin=0, xmax=600000)
plt.show()
