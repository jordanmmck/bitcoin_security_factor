import requests
import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt


# get data
url = 'https://api.blockchain.info/charts/hash-rate?format=json&timespan=all'

if not os.path.isfile('./hash_rate_data.json'):
    response = requests.get(url)
    content = response.json()
    data = content['values']

    # save data to file
    with open('hash_rate_data.json', 'w') as f:
        json.dump(data, f)

with open('hash_rate_data.json') as f:
    hash_rate_data = json.load(f)


# plot
times = np.array([d['x'] for d in hash_rate_data])
hash_rate = np.array([d['y'] for d in hash_rate_data])

plt.plot(times, hash_rate, linewidth=0.8)

plt.xlabel('Time')
plt.ylabel('Hash rate TH/s')
plt.title('Bitcoin Hash Rate')

# plt.ylim(ymin=0, ymax=5E-6)
# plt.xlim(xmin=0, xmax=1200000)
plt.show()
