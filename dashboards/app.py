import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go


st.set_page_config(
    page_title="Supply Chain Delay Predictor",
    page_icon="📦",
    layout="wide",
)

PALETTE = {
    "bg": "#F3F5F4",
    "surface": "#FFFFFF",
    "text": "#1C2530",
    "muted": "#5B6670",
    "border": "#D8DEDC",
    "accent": "#2E5F74",
    "low": "#2F7D5C",
    "moderate": "#C97A2B",
    "high": "#B23A34",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

#MainMenu, header, footer {{ visibility: hidden; }}

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {PALETTE['text']};
}}

.stApp {{ background-color: {PALETTE['bg']}; }}

/* Route manifest card */
.manifest {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 4px;
    padding: 1.1rem 1.4rem;
}}
.manifest-row {{
    display: flex;
    justify-content: space-between;
    padding: 0.35rem 0;
    border-bottom: 1px solid {PALETTE['border']};
    font-size: 0.92rem;
}}
.manifest-row:last-child {{ border-bottom: none; }}
.manifest-label {{ color: {PALETTE['muted']}; }}
.manifest-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
}}

/* Verdict card */
.verdict {{
    border-radius: 4px;
    padding: 1.1rem 1.4rem;
    border: 1px solid {PALETTE['border']};
    border-left: 4px solid var(--verdict-color);
    background: {PALETTE['surface']};
}}
.verdict-label {{
    font-size: 0.8rem;
    color: {PALETTE['muted']};
    margin-bottom: 0.25rem;
}}
.verdict-text {{ font-size: 1.05rem; font-weight: 500; }}

h5 {{ font-weight: 600; letter-spacing: 0.01em; }}
</style>
""", unsafe_allow_html=True)

st.title("Supply Chain & Logistics Delay Predictor")
st.caption(
    "Estimates SLA violation risk for German FMCG shipments from route, "
    "schedule, and weather data."
)

@st.cache_resource
def load_model():
    return joblib.load("models/xgboost_delay_model.joblib")

try:
    model = load_model()
except Exception as e:
    st.error(f"Couldn't load the model: {e}")
    st.stop()

st.sidebar.header("Shipment parameters")

distance_km = st.sidebar.number_input("Distance (km)", 10.0, 2000.0, 450.0, step=10.0)
expected_duration_hours = st.sidebar.number_input(
    "Expected duration (hours)", 1.0, 48.0, 6.0, step=0.5
)
sla_max_hours = st.sidebar.number_input(
    "SLA max allowed (hours)", 1.0, 60.0, 7.0, step=0.5
)

st.sidebar.subheader("Dispatch schedule")
dispatch_hour = st.sidebar.slider("Dispatch hour", 0, 23, 14)
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dispatch_dayofweek = st.sidebar.selectbox(
    "Day of week", options=list(range(7)), format_func=lambda x: day_names[x]
)
is_weekend = int(dispatch_dayofweek in (5, 6))

st.sidebar.subheader("Weather conditions")
avg_precipitation = st.sidebar.slider("Precipitation (mm)", 0.0, 50.0, 2.5, step=0.5)
avg_wind_speed = st.sidebar.slider("Wind speed (km/h)", 0.0, 100.0, 15.0, step=1.0)

input_data = pd.DataFrame([{
    "distance_km": distance_km,
    "expected_duration_hours": expected_duration_hours,
    "sla_max_hours": sla_max_hours,
    "dispatch_hour": dispatch_hour,
    "dispatch_dayofweek": dispatch_dayofweek,
    "is_weekend": is_weekend,
    "avg_precipitation": avg_precipitation,
    "avg_wind_speed": avg_wind_speed,
}])

# Prediction
try:
    prob = float(model.predict_proba(input_data)[:, 1][0])
except Exception as e:
    st.error(
        "Prediction failed. This usually means the input columns don't match "
        f"what the model was trained on.\n\nDetails: {e}"
    )
    st.stop()

if prob >= 0.6:
    color = PALETTE["high"]
    verdict = "This shipment is likely to miss its SLA window. Consider rerouting or expediting."
elif prob >= 0.3:
    color = PALETTE["moderate"]
    verdict = "Some delay risk. Worth a check-in with the carrier before dispatch."
else:
    color = PALETTE["low"]
    verdict = "On track. No action needed."

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown("##### Route manifest")
    rows = [
        ("Distance", f"{distance_km:.0f} km"),
        ("Expected duration", f"{expected_duration_hours:.1f} hrs"),
        ("SLA window", f"{sla_max_hours:.1f} hrs"),
        ("Dispatch", f"{day_names[dispatch_dayofweek]}, {dispatch_hour:02d}:00"),
        ("Precipitation", f"{avg_precipitation:.1f} mm"),
        ("Wind speed", f"{avg_wind_speed:.0f} km/h"),
    ]
    rows_html = "".join(
        f'<div class="manifest-row"><span class="manifest-label">{label}</span>'
        f'<span class="manifest-value">{value}</span></div>'
        for label, value in rows
    )
    st.markdown(f'<div class="manifest">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("##### What's driving this score")
    st.caption("Top factors behind this specific prediction.")
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        raw_shap = explainer.shap_values(input_data)
        values = raw_shap[1][0] if isinstance(raw_shap, list) else raw_shap[0]
        contrib = (
            pd.Series(values, index=input_data.columns)
            .sort_values(key=abs, ascending=False)
            .head(4)
        )
        bar_fig = go.Figure(go.Bar(
            x=contrib.values,
            y=[c.replace("_", " ") for c in contrib.index],
            orientation="h",
            marker_color=[PALETTE["high"] if v > 0 else PALETTE["low"] for v in contrib.values],
        ))
        bar_fig.update_layout(
            height=210,
            margin=dict(l=0, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="IBM Plex Sans", color=PALETTE["text"]),
            xaxis_title="Impact on delay probability",
        )
        st.plotly_chart(bar_fig, use_container_width=True)
    except Exception:

        importances = (
            pd.Series(model.feature_importances_, index=input_data.columns)
            .sort_values(ascending=False)
            .head(4)
        )
        st.bar_chart(importances)

with right:
    st.markdown("##### Delay risk")
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        number={"suffix": "%", "font": {"size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": PALETTE["surface"],
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "#EAF3EE"},
                {"range": [30, 60], "color": "#FBF0E2"},
                {"range": [60, 100], "color": "#F7E7E6"},
            ],
        },
    ))
    gauge_fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color=PALETTE["text"]),
    )
    st.plotly_chart(gauge_fig, use_container_width=True)

    st.markdown(
        f"""
        <div class="verdict" style="--verdict-color: {color}; border-left-color: {color};">
            <div class="verdict-label">Verdict</div>
            <div class="verdict-text">{verdict}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption(
    "Model: XGBoost classifier trained on historical German FMCG shipment "
    "records. Predictions are estimates, not guarantees — use alongside "
    "carrier judgment."
)
