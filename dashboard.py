import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk

# --- Constants for color buckets ---
ADOPTION_BUCKETS = [
    (0, 10, "#FF4B4B"),      # Red
    (11, 25, "#FFA500"),     # Orange
    (26, 50, "#FFD700"),     # Yellow
    (51, 75, "#90EE90"),     # Light Green
    (76, 100, "#228B22"),    # Dark Green
]

# --- Helper functions ---
def get_adoption_color(adoption_pct):
    for low, high, color in ADOPTION_BUCKETS:
        if low <= adoption_pct <= high:
            return color
    return "#CCCCCC"

def parse_adoption_pct(val):
    if isinstance(val, str):
        return float(val.replace("%", ""))
    return float(val)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("CSU_Campus_Adoption_with_Coordinates.csv")
    df["Adoption %"] = df["Adoption %"].apply(parse_adoption_pct)
    return df

df = load_data()

# --- Session State for What-If ---
if "whatif_mode" not in st.session_state:
    st.session_state["whatif_mode"] = False
if "slider_values" not in st.session_state:
    st.session_state["slider_values"] = df["Active Users"].tolist()

def reset_sliders():
    st.session_state["slider_values"] = df["Active Users"].tolist()

# --- Top Bar: What-If Mode Toggle & Reset ---
topcol1, topcol2 = st.columns([1, 1])
with topcol1:
    st.checkbox(
        "Enable What-If Mode",
        value=st.session_state["whatif_mode"],
        key="whatif_mode"
    )
with topcol2:
    if st.button("Reset to CSV"):
        reset_sliders()

# --- Use What-If or Actual Data ---
if st.session_state["whatif_mode"]:
    active_users = st.session_state["slider_values"]
else:
    active_users = df["Active Users"].tolist()

df_display = df.copy()
df_display["Active Users"] = active_users
df_display["Adoption %"] = np.round(
    100 * df_display["Active Users"] / df_display["Total Users"], 1
)

# --- Global Adoption Gauge ---
total_active = sum(df_display["Active Users"])
total_users = sum(df_display["Total Users"])
global_pct = 100 * total_active / total_users if total_users > 0 else 0

st.title("CSU Campus Adoption Dashboard")

gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=global_pct,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "System-wide Adoption %"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': get_adoption_color(global_pct)},
        'steps': [
            {'range': [0, 10], 'color': "#FF4B4B"},
            {'range': [10, 25], 'color': "#FFA500"},
            {'range': [25, 50], 'color': "#FFD700"},
            {'range': [50, 75], 'color': "#90EE90"},
            {'range': [75, 100], 'color': "#228B22"},
        ],
    }
))
st.plotly_chart(gauge_fig, use_container_width=True)

# --- Interactive Map ---
st.subheader("Campus Adoption Map")
map_df = df_display.copy()
# All circles transparent red
map_df["color"] = [[255, 0, 0, 80]] * len(map_df)
map_df["size"] = np.clip(map_df["Total Users"] / 1000, 5, 30)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[Longitude, Latitude]',
    get_radius="size * 1000",
    get_fill_color="color",
    pickable=True,
    auto_highlight=True,
)

# Focus on all of California, fixed view, light map style, no zoom/pan
view_state = pdk.ViewState(
    latitude=36.5,
    longitude=-119.5,
    zoom=5.2,
    min_zoom=5.2,
    max_zoom=5.2,
    pitch=0,
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v9",
    tooltip={
        "html": "<b>{Campus}</b><br/>Total Users: {Total Users}<br/>Active Users: {Active Users}<br/>Adoption %: {Adoption %}%",
        "style": {"color": "black", "backgroundColor": "white"}
    }
)
st.pydeck_chart(r, use_container_width=True)

# --- Campus Cards/Grid with What-If Sliders ---
st.subheader("Campus Details & What-If Simulation")

cols = st.columns(3)
for idx, row in df_display.iterrows():
    with cols[idx % 3]:
        with st.container():
            st.markdown(
                f"""
                <style>
                .campus-box-{idx} {{
                    background: #23272b;
                    border: 2px solid #888;
                    border-radius: 18px;
                    padding: 0.7em 0.5em 0.5em 0.5em;
                    margin-bottom: 1.2em;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                    text-align: center;
                }}
                </style>
                <div class="campus-box-{idx}">
                <div style='font-size:1.1em; font-weight:600; margin-bottom:0.2em; color:#fff'>{row['Campus']}</div>
                """,
                unsafe_allow_html=True
            )
            campus_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=row["Adoption %"],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Adoption %", 'font': {'size': 12, 'color': '#fff'}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1976D2"},
                    'steps': [
                        {'range': [0, 10], 'color': "#FF4B4B"},
                        {'range': [10, 25], 'color': "#FFA500"},
                        {'range': [25, 50], 'color': "#FFD700"},
                        {'range': [50, 75], 'color': "#90EE90"},
                        {'range': [75, 100], 'color': "#228B22"},
                    ],
                },
                number={'suffix': "%", 'font': {'size': 18, 'color': '#fff'}}
            ))
            campus_gauge.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=180,
                paper_bgcolor="#23272b",
                font_color="#fff"
            )
            st.plotly_chart(campus_gauge, use_container_width=True)
            st.markdown(
                f"<div style='margin-top:-1.2em; margin-bottom:0.5em; color:#fff'><b>Active Users:</b><br>{row['Active Users']} / {row['Total Users']}</div>",
                unsafe_allow_html=True
            )
            if st.session_state["whatif_mode"]:
                slider_val = st.slider(
                    f"Set Active Users for {row['Campus']}",
                    min_value=0,
                    max_value=int(row["Total Users"]),
                    value=int(st.session_state["slider_values"][idx]),
                    key=f"slider_{idx}"
                )
                st.session_state["slider_values"][idx] = slider_val
            st.markdown("</div>", unsafe_allow_html=True)

st.caption("No data is saved. Reset restores original CSV values.")