import redis
import os
import json
import time
from datetime import datetime
from collections import defaultdict

REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
try:
    redis_client = redis.Redis.from_url(REDIS_URI)
except Exception:
    redis_client = None

ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), '../logs/analytics.jsonl')

def log_event(event_type, payload):
    event = {
        'type': event_type,
        'payload': payload,
        'timestamp': datetime.utcnow().isoformat()
    }
    if redis_client:
        try:
            redis_client.xadd('analytics', event)
            return
        except Exception:
            pass
    # Fallback to file
    with open(ANALYTICS_FILE, 'a') as f:
        f.write(json.dumps(event) + '\n')

class AnalyticsTracker:
    def __init__(self):
        self.redis = redis_client
        self.file_path = 'logs/analytics.jsonl'

    def log_event(self, event_type, data):
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        # Log to Redis stream
        if self.redis:
            try:
                self.redis.xadd('analytics', event)
            except Exception:
                self._log_to_file(event)
        else:
            self._log_to_file(event)

    def _log_to_file(self, event):
        with open(self.file_path, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def export_events(self, fmt='json'):
        # Export all events from file (for demo)
        events = []
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                for line in f:
                    events.append(json.loads(line))
        if fmt == 'csv':
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=events[0].keys())
            writer.writeheader()
            for e in events:
                writer.writerow(e)
            return output.getvalue()
        return json.dumps(events, indent=2)

    def aggregate(self):
        # Simple aggregation for demo
        stats = defaultdict(int)
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                for line in f:
                    e = json.loads(line)
                    t = e['type']
                    stats[t] += 1
        return dict(stats) 