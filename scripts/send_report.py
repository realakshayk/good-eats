from core.analytics import AnalyticsTracker
from datetime import datetime
tracker = AnalyticsTracker()
stats = tracker.aggregate()
print(f"[Report] {datetime.now().isoformat()}\nTop Events:")
for k, v in stats.items():
    print(f"{k}: {v}")
print("(Stub: send via email/Slack/SendGrid)") 