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


# get data
if not os.path.isfile('./block_data.json'):
    get_data()

with open('block_data.json') as f:
    block_data = json.load(f)


# set security factor figures for existing blocks
for block in block_data:
    supply = block['supply']
    if supply == 0:
        block['fee_security_factor'] = 0
        block['block_reward_security_factor'] = 0
    else:
        block['fee_security_factor'] = block['reward_fees'] / supply
        block['block_reward_security_factor'] = block['reward_block'] / supply


# project block rewards for future blocks
block_num = block_data[-1]['block']
block_reward = block_data[-1]['reward_block']
supply = block_data[-1]['supply'] + block_data[-1]['reward_block']
upper_limit = 800000
projected_rewards = []
for block_num in range(block_num+1, upper_limit):
    if block_num % 210000 == 0:
        block_reward /= 2
    try:
        block_reward_sf = block_reward / supply
    except ZeroDivisionError:
        block_reward_sf = 0
    block = {
                "block_num": block_num,
                "block_reward_sf": block_reward_sf
            }
    supply += block_reward
    projected_rewards.append(block)


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

# plot
plt.plot(blocks_arr, block_rewards_arr)
plt.plot(blocks_arr, fee_rewards_arr, color='grey', linewidth=0.2)
plt.plot(blocks_arr, line, color='red')
plt.ylim(ymin=0, ymax=5E-6)
plt.xlim(xmin=0, xmax=600000)
plt.show()
