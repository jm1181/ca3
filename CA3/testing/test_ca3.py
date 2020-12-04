from ca3 import news, weather, corona, alarm
import json

with open('config.json', 'r') as f:
    json_file = json.load(f)
API_keys = json_file["API_keys"]
location = json_file["location"]


def tests():
    assert news(API_keys[news]) == API_keys[news]
