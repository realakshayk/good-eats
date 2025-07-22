from core.analytics import AnalyticsTracker
import argparse
parser = argparse.ArgumentParser(description='Export analytics events.')
parser.add_argument('--format', choices=['json', 'csv'], default='json')
args = parser.parse_args()
tracker = AnalyticsTracker()
print(tracker.export_events(fmt=args.format)) 