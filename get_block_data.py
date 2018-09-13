import requests
import json
import time


latest_block_url = 'https://blockchain.info/latestblock'
block_data_url = 'https://chain.api.btc.com/v3/block/{}'
data_file_name = 'data/block_data.json'

START_BLOCK = 0
BATCH_SIZE = 50

def update_data():
    print('Updating block data...')

    with open('data/block_data.json') as f:
        data = json.load(f)

    latest_block_downloaded = data[-1]['block']
    response = requests.get(latest_block_url)
    latest_block_available = response.json()['height']

    for block_num in range(latest_block_downloaded+1, latest_block_available):
        print('Downloading block: {}'.format(block_num))
        while True:
            try:
                response = requests.get(block_data_url.format(block_num))
            except:
                print('Timed out, retrying...')
                time.sleep(30)
                continue
            if not response.status_code == 200:
                print('Request failed, retrying...')
                time.sleep(30)
                continue
            break

        block = response.json()['data']
        data.append({
                    "block": block['height'],
                    "timestamp": block['curr_max_timestamp'],
                    "block_reward": block['reward_block'],
                    "fees": block['reward_fees'],
                })

    with open('data/block_data.json', 'w') as f:
        json.dump(data, f)
    print('Up to date.')


def get_data():
    print('Getting Data...')
    print('---------------------')
    response = requests.get(latest_block_url)
    latest_block = response.json()['height']

    data = []

    # get data
    t0 = time.time()
    for batch in range(START_BLOCK, latest_block, BATCH_SIZE):
        url_options_list = [str(i) for i in range(batch, batch+BATCH_SIZE)]
        batch_url = block_data_url.format(','.join(url_options_list))
        response = requests.get(batch_url)

        # wait then retry if request failed
        while not response.status_code == 200:
            print('Request failed, retrying...')
            time.sleep(30)
            response = requests.get(batch_url)
        content = response.json()

        # append relevant data to list
        for block in content['data']:
            try:
                data.append({
                            "block": block['height'],
                            "timestamp": block['curr_max_timestamp'],
                            "block_reward": block['reward_block'],
                            "fees": block['reward_fees'],
                        })
            except TypeError:
                break

        elapsed_time = time.time() - t0
        print('blocks: {}, time: {:.4f}, progress: {:.2f}%'.format(
            batch+BATCH_SIZE, 
            elapsed_time,
            (batch+BATCH_SIZE)/latest_block*100
        ))

    # save data to file
    with open(data_file_name, 'w') as f:
        json.dump(data, f)

    print('---------------------')
    print('Data saved to {}'.format(data_file_name))
