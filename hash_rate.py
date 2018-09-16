import requests
import json
import os
import sys
import datetime as dt

import numpy as np
import matplotlib.pyplot as plt


# get data
url = 'https://api.blockchain.info/charts/hash-rate?format=json&timespan=all'

if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.isfile('data/hash_rate_data.json'):
    response = requests.get(url)
    content = response.json()
    data = content['values']

    # save data to file
    with open('data/hash_rate_data.json', 'w') as f:
        json.dump(data, f)

with open('data/hash_rate_data.json') as f:
    hash_rate_data = json.load(f)

# add datetimes from unix times
for data_point in hash_rate_data:
    data_point['datetime'] = dt.datetime.fromtimestamp(data_point['x'])

# plot
datetimes = np.array([d['datetime'] for d in hash_rate_data])
hash_rate = np.array([d['y'] for d in hash_rate_data])
plt.plot(datetimes, hash_rate, color='#2a51fc', linewidth=1)

ax = plt.gca()
ylabels = [format(label, ',.0f') for label in ax.get_yticks()]
ax.set_yticklabels(ylabels)

plt.xlabel('Year')
plt.ylabel('Hash Rate TH/s')
plt.title('Bitcoin Hash Rate')

fig = plt.gcf()
fig.set_size_inches(14.5, 8.5)
fig.savefig('figures/hash_rate.png', dpi=100, bbox_inches='tight')
