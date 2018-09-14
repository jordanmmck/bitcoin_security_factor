import requests
import json
import os
import sys
import datetime as dt

import numpy as np
import matplotlib.pyplot as plt


# get data
url = 'https://api.blockchain.info/charts/miners-revenue?format=json&timespan=all'

if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.isfile('data/miner_revenue_data.json'):
    response = requests.get(url)
    content = response.json()
    data = content['values']

    with open('data/miner_revenue_data.json', 'w') as f:
        json.dump(data, f)


with open('data/miner_revenue_data.json') as f:
    miner_revenue_data = json.load(f)

# add datetimes from unix times
for data_point in miner_revenue_data:
    data_point['datetime'] = dt.datetime.fromtimestamp(data_point['x'])

# plot
times = np.array([d['x'] for d in miner_revenue_data])
datetimes = np.array([d['datetime'] for d in miner_revenue_data])
miner_revenue = np.array([d['y'] for d in miner_revenue_data])

plt.plot(datetimes, miner_revenue, color='#2a51fc', linewidth=1)

ax = plt.gca()
ylabels = [format(label, ',.0f') for label in ax.get_yticks()]
ax.set_yticklabels(ylabels)

plt.xlabel('Year')
plt.ylabel('USD')
plt.title('Bitcoin Total Daily Miner Revenue')

fig = plt.gcf()
fig.set_size_inches(14.5, 8.5)
fig.savefig('figures/miner_revenue.png', dpi=200, bbox_inches='tight')
