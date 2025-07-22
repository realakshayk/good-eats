import streamlit as st
import httpx
import json
import time
from streamlit_folium import st_folium
import folium
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/meals/find")

st.set_page_config(page_title="Good Eats - Meal Finder", layout="wide")
st.title("🥗 Good Eats: AI-Powered Meal Discovery")

# Sidebar: Goal selection, radius, macros, exclusions, flavor prefs
goal_options = {
    "muscle_gain": "High protein (30–40%), 2500–3500 cal, moderate carbs/fats",
    "weight_loss": "1500–2000 cal, 25–30% protein, low carbs, moderate fats",
    "keto": "5–10% carbs, 70–80% fat, moderate protein, 1800–2200 cal",
    "balanced": "2000–2500 cal with balanced macros (30/40/30)",
    "athletic_endurance": "3000–4000 cal, higher carbs (50–60%), moderate protein/fat",
    "vegan_protein": "2000–2400 cal, high plant protein, low/medium fat"
}

with st.sidebar:
    st.header("Search Settings")
    goal = st.selectbox("Fitness Goal", list(goal_options.keys()), format_func=lambda k: f"{k.replace('_',' ').title()} — {goal_options[k]}")
    radius = st.slider("Search Radius (miles)", 0.5, 10.0, 3.0, 0.5)
    macro_override = st.checkbox("Override Macros?")
    macros = {}
    if macro_override:
        macros["min_calories"] = st.number_input("Min Calories", 0, 5000, 1200)
        macros["max_calories"] = st.number_input("Max Calories", 0, 5000, 2500)
        macros["min_protein"] = st.number_input("Min Protein (g)", 0, 300, 20)
        macros["max_protein"] = st.number_input("Max Protein (g)", 0, 300, 200)
    flavor_prefs = st.multiselect("Flavor Preferences", ["spicy", "umami", "sweet", "sour", "salty"])
    exclude_ingredients = st.text_input("Exclude Ingredients (comma-separated)")
    st.markdown("---")
    st.caption("Powered by Good Eats AI")

# Geolocation (browser or manual)
if "location" not in st.session_state:
    st.session_state["location"] = {"lat": 40.7128, "lon": -74.0060}

with st.expander("Location Settings", expanded=False):
    use_geo = st.checkbox("Use browser geolocation", value=True)
    if use_geo:
        st.info("Browser geolocation not available in Streamlit. Enter manually below.")
    lat = st.number_input("Latitude", -90.0, 90.0, st.session_state["location"]["lat"])
    lon = st.number_input("Longitude", -180.0, 180.0, st.session_state["location"]["lon"])
    st.session_state["location"] = {"lat": lat, "lon": lon}

# Search button
if st.button("🔍 Find Meals"):
    payload = {
        "location": st.session_state["location"],
        "goal": goal,
        "radius": radius,
        "override_macros": macros if macro_override else None,
        "flavor_preferences": flavor_prefs,
        "exclude_ingredients": [x.strip() for x in exclude_ingredients.split(",") if x.strip()]
    }
    st.session_state["last_payload"] = payload
    st.session_state["searching"] = True
    st.session_state["results"] = None
    st.session_state["error"] = None

# API call and results
def fetch_meals(payload):
    try:
        start = time.time()
        with httpx.Client(timeout=20) as client:
            resp = client.post(API_URL, json=payload, headers={"X-API-Key": "test-free-key"})
        latency = time.time() - start
        if resp.status_code == 200:
            return resp.json(), latency, None
        else:
            return None, latency, resp.text
    except Exception as e:
        return None, 0, str(e)

if st.session_state.get("searching"):
    with st.spinner("Searching for meals..."):
        results, latency, error = fetch_meals(st.session_state["last_payload"])
        st.session_state["searching"] = False
        if error:
            st.session_state["error"] = error
        else:
            st.session_state["results"] = results
            st.session_state["latency"] = latency

# Error banner
if st.session_state.get("error"):
    st.error(f"Error: {st.session_state['error']}")
    if st.button("Retry"):
        st.session_state["searching"] = True
        st.session_state["error"] = None

# Results grid
if st.session_state.get("results") and st.session_state["results"].get("meals"):
    st.subheader(f"Results ({len(st.session_state['results']['meals'])} meals found)")
    if st.session_state.get("latency"):
        st.caption(f"Response time: {st.session_state['latency']:.2f}s")
    cols = st.columns(3)
    for i, meal in enumerate(st.session_state["results"]["meals"]):
        with cols[i % 3]:
            st.markdown(f"### {meal['name']}")
            st.markdown(f"_{meal['description']}_")
            st.markdown(f"**Price:** {meal.get('price','N/A')}")
            st.markdown(f"**Tags:** {' '.join(meal.get('tags', []))}")
            st.markdown(f"**Score:** {meal.get('relevance_score', 0):.2f}")
            st.markdown(f"**Confidence:** {meal.get('confidence_level', 'N/A')}")
            if st.button("⭐ Favorite", key=f"fav_{i}"):
                st.success("Favorited!")
            with st.expander("Nutrition Breakdown"):
                st.json(meal.get('nutrition', {}))
            with st.expander("Score Details"):
                st.json(meal.get('score_breakdown', {}))

    # Macro breakdown chart (horizontal bar)
    st.subheader("Macro Breakdown (Top Meal)")
    top_meal = st.session_state["results"]["meals"][0]
    macros = top_meal.get('nutrition', {})
    st.bar_chart({
        "Protein": [macros.get('protein', 0)],
        "Carbs": [macros.get('carbs', 0)],
        "Fat": [macros.get('fat', 0)]
    })

    # Nutrition radar chart (spider)
    try:
        import plotly.graph_objects as go
        st.subheader("Nutrition Radar Chart (Top Meal)")
        fig = go.Figure()
        categories = ['protein', 'carbs', 'fat']
        values = [macros.get(cat, 0) for cat in categories]
        fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name='Macros'))
        st.plotly_chart(fig)
    except ImportError:
        st.info("Install plotly for radar charts: pip install plotly")

    # Map of restaurants
    st.subheader("Restaurant Map")
    m = folium.Map(location=[st.session_state["location"]["lat"], st.session_state["location"]["lon"]], zoom_start=13)
    for meal in st.session_state["results"]["meals"]:
        rest = meal.get('restaurant', {})
        if rest.get('name') and rest.get('place_id'):
            folium.Marker(
                [rest.get('lat', st.session_state["location"]["lat"]), rest.get('lon', st.session_state["location"]["lon"])],
                popup=rest.get('name'),
                tooltip=rest.get('address', rest.get('name'))
            ).add_to(m)
    st_folium(m, width=700, height=400) 