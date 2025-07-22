import httpx
import argparse
import json
import time

parser = argparse.ArgumentParser(description="Profile meal discovery API response times.")
parser.add_argument('--url', required=True, help='Discovery endpoint URL')
parser.add_argument('--payload', required=True, help='JSON payload file')
parser.add_argument('--api-key', default='test-free-key', help='API key header')
parser.add_argument('--iterations', type=int, default=5, help='Number of requests')
args = parser.parse_args()

headers = {'X-API-Key': args.api_key}
with open(args.payload, 'r') as f:
    data = json.load(f)

times = []
with httpx.Client() as client:
    for i in range(args.iterations):
        start = time.time()
        resp = client.post(args.url, json=data, headers=headers)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Run {i+1}: {elapsed:.2f}s Status: {resp.status_code}")
print(f"Avg: {sum(times)/len(times):.2f}s Min: {min(times):.2f}s Max: {max(times):.2f}s") 