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


with open('block_data.json') as f:
    block_data = json.load(f)

pp = pprint.PrettyPrinter(depth=2)
pp.pprint(block_data[500000])

for block in block_data:
    block['miner_revenue'] = block['reward_block'] + block['reward_fees']
    supply = block['supply']
    if supply == 0:
        block['fee_security_factor'] = 0
        block['block_reward_security_factor'] = 0
        block['security_factor'] = 0
    else:
        block['fee_security_factor'] = block['reward_fees'] / supply
        block['block_reward_security_factor'] = block['reward_block'] / supply
        block['security_factor'] = block['miner_revenue'] / supply

pp.pprint(block_data[500000:500005])

# SATOSHI_FACTOR = 1E8

# # construct supply schedule data
# reward = 50 * SATOSHI_FACTOR
# supply = 0
# blocks = []
# for block in range(2000000):
#     try:
#         daily_inflation = reward * BLOCKS_PER_DAY / supply
#     except ZeroDivisionError:
#         daily_inflation = math.inf
#     blocks.append({
#             'block': block, 
#             'supply': supply, 
#             'block_reward': reward,
#             'daily_inflation': daily_inflation,
#             'daily_fee': None,
#             'daily_fee_ratio': None,
#             'date': None,
#             'unix_date': None
#         })
#     if block % 210000 == 0 and block > 0:
#         reward = reward//2
#     supply += reward


blocks_arr = np.array([d['block'] for d in block_data])
block_rewards_arr = np.array([d['block_reward_security_factor'] for d in block_data])
fee_rewards_arr = np.array([d['fee_security_factor'] for d in block_data])
security_factor_arr = np.array([d['security_factor'] for d in block_data])
# fees_arr = np.array([d['daily_fee_ratio'] for d in blocks])
# inflations_arr = np.array([d['daily_inflation'] for d in blocks])

slope, intercept, r_value, p_value, std_err = stats.linregress(blocks_arr, fee_rewards_arr)
line = slope*blocks_arr+intercept
print(slope, intercept)

# # plt.ylim(ymin=1E-12, ymax=1E1)
# # # plt.semilogy(blocks_arr, inflations_arr)
# # plt.ylim(ymin=0, ymax=5E-5)
plt.plot(blocks_arr, block_rewards_arr)
plt.plot(blocks_arr, fee_rewards_arr, color='grey', linewidth=0.2)
plt.plot(blocks_arr, line, color='red')
plt.ylim(ymin=0, ymax=5E-6)
plt.xlim(xmin=0, xmax=600000)
# # plt.scatter(blocks_arr, fees_arr, s=0.5)
plt.show()
