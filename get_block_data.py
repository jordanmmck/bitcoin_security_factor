import requests
import json
import time


base_url = 'https://chain.api.btc.com/v3/block/{}'
data = []

t0 = time.time()
start_block = 0
end_block = 540950
for batch in range(start_block,end_block,50):
    url_op_num_list = [str(i) for i in range(batch,batch+50)]
    batch_url = base_url.format(','.join(url_op_num_list))
    response = requests.get(batch_url)
    delay = 1
    while not response.status_code == 200:
        time.sleep(delay * 15)
        delay += 1
        response = requests.get(batch_url)

    content = response.json()
    for block in content['data']:
        data.append({
                    "block": block['height'],
                    "timestamp": block['curr_max_timestamp'],
                    "reward_block": block['reward_block'],
                    "reward_fees": block['reward_fees'],
                })
    t1 = time.time()
    elapsed_time = t1 - t0
    print('blocks: {}, time: {:.4f}, progress: {:.2f}%'.format(
        batch+50, 
        elapsed_time,
        (batch+50)/end_block
    ))

with open('fee_data.json', 'w') as f:
    json.dump(data, f)
