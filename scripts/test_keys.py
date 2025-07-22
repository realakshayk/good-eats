import os
import requests
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')
google_key = os.getenv('GOOGLE_API_KEY')

print('Testing OpenAI key...')
try:
    openai.Model.list()
    print('OpenAI key valid.')
except Exception as e:
    print('OpenAI key failed:', e)

print('Testing Google Places key...')
try:
    resp = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params={
        'location': '40.7128,-74.0060', 'radius': 1000, 'type': 'restaurant', 'key': google_key
    })
    if resp.status_code == 200 and 'results' in resp.json():
        print('Google key valid.')
    else:
        print('Google key failed:', resp.text)
except Exception as e:
    print('Google key failed:', e) 