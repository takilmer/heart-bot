import time, datetime
from posixpath import join as urljoin
import requests
import pandas as pd
import matplotlib.pyplot as plt


token = '6ipjbRMVOeLbexP83M5tBpvD471YhtHd0GOIgvmZ'
bot_id = '24b5cb92c298e2b3e6e81ec593'
group_id = 60402884

base_url = 'https://api.groupme.com/v3'

def s_datetime(ms):
    return datetime.datetime(1970,1,1) + datetime.timedelta(0, ms)

def get_liked_messages():
    url = urljoin(base_url, f'groups/{group_id}/likes')
    params = {'token': token, 'period':'month'}
    response = requests.get(url=url, params=params)
    assert response.status_code == 200, 'get_liked_messages request failed: ' + str(response.json()['meta'])
    return response.json()['response']['messages']


def remove_self_likes(msg):
    users = [usr for usr in msg['favorited_by'] if usr != msg['user_id']]
    msg['favorited_by'] = users


def get_messages():
    messages = []
    before_id = None
    url = urljoin(base_url, f'groups/{group_id}/messages')
    while True:
        params = {'token': token, 'limit': 100, 'before_id': before_id}
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            break
        msg_list = response.json()['response']['messages']
        messages += msg_list
        before_id = msg_list[-1]['id']
    return messages

messages = get_messages()
for msg in messages:
    #remove_self_likes(msg)
    pass
df = pd.DataFrame(messages)

df['timestamp'] = df['created_at'].apply(s_datetime)
df.sort_values('timestamp', ascending=False, inplace=True)
df['total_likes'] = df['favorited_by'].str.len()
columns = ['id', 'name', 'sender_id', 'text', 'user_id', 'timestamp', 'total_likes']
df = df[columns]

id_map = df.drop_duplicates('sender_id')[['sender_id', 'name']].set_index('sender_id')
last_message_time = df['timestamp'].min()
user_likes = df.groupby('sender_id')['total_likes'].sum()
user_likes = pd.concat([user_likes, id_map], axis=1).set_index('name')

fig = user_likes.query('total_likes > 0').plot(kind='pie', y='total_likes', legend=False)
plt.savefig('./pics/chart.png')

