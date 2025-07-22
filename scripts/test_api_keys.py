import yaml
import os
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/api_keys.yaml')
with open(CONFIG_PATH, 'r') as f:
    data = yaml.safe_load(f)
    keys = data.get('api_keys', {})
    for k, v in keys.items():
        print(f"Key: {k} | Plan: {v['plan']} | Description: {v.get('description','')}") 