import httpx
import argparse
import json

parser = argparse.ArgumentParser(description="Test API endpoint.")
parser.add_argument('--url', required=True, help='Endpoint URL')
parser.add_argument('--method', default='POST', help='HTTP method')
parser.add_argument('--payload', default=None, help='JSON payload file')
parser.add_argument('--api-key', default='test-free-key', help='API key header')
args = parser.parse_args()

headers = {'X-API-Key': args.api_key}

if args.payload:
    with open(args.payload, 'r') as f:
        data = json.load(f)
else:
    data = {}

with httpx.Client() as client:
    method = args.method.upper()
    if method == 'POST':
        resp = client.post(args.url, json=data, headers=headers)
    else:
        resp = client.get(args.url, params=data, headers=headers)
    print(f"Status: {resp.status_code}")
    print(resp.text) 