import streamlit as st
import json
import os
from collections import Counter, defaultdict

st.set_page_config(page_title="Good Eats Analytics Dashboard", layout="wide")
st.title("📊 Good Eats Analytics Dashboard")

log_path = 'logs/analytics.jsonl'
events = []
if os.path.exists(log_path):
    with open(log_path) as f:
        for line in f:
            events.append(json.loads(line))

st.write(f"Loaded {len(events)} events.")

# Top goals
goal_searches = [e['data']['goal'] for e in events if e['type'] == 'goal_search']
goal_counts = Counter(goal_searches)
st.subheader("Top Fitness Goals Searched")
st.bar_chart(goal_counts)

# API call volume
api_calls = [e['data']['endpoint'] for e in events if e['type'] == 'api_timing']
api_counts = Counter(api_calls)
st.subheader("API Call Volume by Endpoint")
st.bar_chart(api_counts)

# Error rates
error_events = [e for e in events if e['type'] == 'error']
st.subheader("Error Events")
st.write(f"Total errors: {len(error_events)}")

# Macro trends (demo)
macro_totals = defaultdict(int)
for e in events:
    if e['type'] == 'meal_view' and 'nutrition' in e['data']:
        n = e['data']['nutrition']
        for k in ['protein', 'carbs', 'fat']:
            macro_totals[k] += n.get(k, 0)
st.subheader("Macro Trends (Total)")
st.bar_chart(macro_totals)

# Download/export
st.download_button("Export Events (JSON)", json.dumps(events, indent=2), file_name="analytics.json", mime="application/json") 