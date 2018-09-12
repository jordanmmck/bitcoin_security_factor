import requests
import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt


# get data
url = 'https://api.blockchain.info/charts/miners-revenue?format=json&timespan=all'

if not os.path.isfile('./miner_revenue_data.json'):
    response = requests.get(url)
    content = response.json()
    data = content['values']

    # save data to file
    with open('miner_revenue_data.json', 'w') as f:
        json.dump(data, f)

with open('miner_revenue_data.json') as f:
    miner_revenue_data = json.load(f)


# plot
times = np.array([d['x'] for d in miner_revenue_data])
miner_revenue = np.array([d['y'] for d in miner_revenue_data])

plt.plot(times, miner_revenue, linewidth=0.8)

plt.xlabel('Time')
plt.ylabel('Revenue $/day')
plt.title('Total Miner Revenue')

plt.show()
