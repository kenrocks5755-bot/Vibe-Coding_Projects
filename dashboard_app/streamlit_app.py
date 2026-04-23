import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json

# Set page configuration
st.set_page_config(
    page_title="LORI Environmental Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 1. Load and prepare the dataset
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    data['Month'] = pd.Categorical(data['Month'], categories=month_order, ordered=True)
    return data.sort_values(['City', 'Month'])

data = load_data("dataset.csv")

# 2. Configuration Data
state_mapping = {
    "Mumbai": {"name": "Maharashtra", "coords": [19.0760, 72.8777], "zoom": 6},
    "Delhi": {"name": "Delhi", "coords": [28.6139, 77.2090], "zoom": 9},
    "Bangalore": {"name": "Karnataka", "coords": [12.9716, 77.5946], "zoom": 6},
    "Chennai": {"name": "Tamil Nadu", "coords": [13.0827, 80.2707], "zoom": 6},
    "Kolkata": {"name": "West Bengal", "coords": [22.5726, 88.3639], "zoom": 6}
}

month_options = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
month_mapping = {
    "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
    "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
    "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec"
}

# 3. Floating User Inputs (using hidden sidebar or top controls)
# Since we want a "glassy" overlay look, we put selectboxes in a specific container later,
# but we need the values now to filter.
# We'll use Streamlit's session state for clean updates.
if 'city' not in st.session_state: st.session_state.city = "Mumbai"
if 'month_full' not in st.session_state: st.session_state.month_full = "January"

city = st.session_state.city
month_full = st.session_state.month_full
month_abbr = month_mapping[month_full]

# 4. Filter Data
city_data = data[data['City'] == city]
month_data = city_data[city_data['Month'] == month_abbr].iloc[0]

# 5. Generate Enhanced 2D Premium Charts
def create_enhanced_charts(city_data, city_name, current_month):
    # Temperature Trend (Avg vs Max)
    fig_temp = go.Figure()
    
    # Max Temp Trace
    fig_temp.add_trace(go.Scatter(
        x=month_options, y=city_data['Max_Temp'],
        mode='lines+markers', name='Max Temp',
        line=dict(color='rgba(236, 72, 153, 0.4)', width=2, dash='dot', shape='spline'),
        marker=dict(size=6, opacity=0.4)
    ))
    
    # Avg Temp Trace
    fig_temp.add_trace(go.Scatter(
        x=month_options, y=city_data['Avg_Temp'],
        mode='lines+markers', name='Avg Temp',
        line=dict(color='#6366f1', width=5, shape='spline'),
        marker=dict(size=8, color='#6366f1', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    ))
    
    # Vertical Line for Selected Month
    fig_temp.add_vline(x=current_month, line_width=2, line_dash="dash", line_color="#f8fafc")

    fig_temp.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10), height=250,
        xaxis=dict(showgrid=False, color='#94a3b8', tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#94a3b8'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94a3b8"))
    )

    # AQI Trend
    fig_aqi = go.Figure()
    fig_aqi.add_trace(go.Scatter(
        x=month_options, y=city_data['AQI'],
        mode='lines+markers', name='AQI',
        line=dict(color='#ec4899', width=5, shape='spline'),
        marker=dict(size=8, color='#ec4899', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(236, 72, 153, 0.1)'
    ))
    
    fig_aqi.add_vline(x=current_month, line_width=2, line_dash="dash", line_color="#f8fafc")

    fig_aqi.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10), height=250,
        xaxis=dict(showgrid=False, color='#94a3b8', tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#94a3b8'),
        showlegend=False
    )
    return fig_temp, fig_aqi

fig_temp, fig_aqi = create_enhanced_charts(city_data, city, month_full)


# 6. Custom CSS for Classic Layout
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');

:root {
    --primary: #6366f1;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --glass-border: rgba(255, 255, 255, 0.1);
}

.stApp {
    background-color: #020617;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
        radial-gradient(at 0% 100%, rgba(99, 102, 241, 0.15) 0px, transparent 50%);
    background-attachment: fixed;
    background-size: cover;
    color: var(--text-main);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Classic card styling */
.card {
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem;
    height: 100%;
}

.header-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 0px; }
.header-sub { font-size: 1.1rem; color: #94a3b8; margin-bottom: 2rem; }

/* Metadata styling */
.meta-item { margin-bottom: 1rem; }
.meta-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
.meta-value { font-size: 1.2rem; font-weight: 600; color: #fff; }

/* Hide standard streamlit elements */
[data-testid="stHeader"], [data-testid="stFooter"] { display: none; }
</style>
""", unsafe_allow_html=True)

# 7. Enhanced Background Map Template
current_state = state_mapping[city]
leaflet_html = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
    <style>
        body, html, #map {{ height: 100%; margin: 0; background: #020617; overflow: hidden; border-radius: 16px; }}
        .leaflet-tile-pane {{ filter: brightness(0.6) contrast(1.2) sepia(100%) hue-rotate(180deg) saturate(200%); }}
        .neon-label {{
            background: rgba(15, 23, 42, 0.9); color: #60a5fa; padding: 8px 12px; border-radius: 8px;
            font-size: 12px; font-weight: 800; border: 1px solid #3b82f6; backdrop-filter: blur(4px);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
            text-align: center;
        }}
        .neon-label .temp {{ font-size: 16px; color: #fff; display: block; margin-top: 4px; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map', {{ center: {current_state['coords']}, zoom: {current_state['zoom']}, zoomControl: true, attributionControl: false }});
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
        
        // Heatmap layer for all cities based on Avg Temp
        const heatPoints = {json.dumps([[state_mapping[c]['coords'][0], state_mapping[c]['coords'][1], float(data[(data['City']==c) & (data['Month']==month_abbr)]['Avg_Temp'].iloc[0])] for c in data['City'].unique()])};
        L.heatLayer(heatPoints.map(p => [p[0], p[1], (p[2]-15)/35]), {{ radius: 80, blur: 40, maxZoom: 1 }}).addTo(map);
        
        // Detailed Marker
        L.marker({current_state['coords']}, {{ 
            icon: L.divIcon({{ 
                className: 'city-label', 
                html: '<div class="neon-label">{city} <span class="temp">{month_data["Avg_Temp"]}°C</span></div>',
                iconSize: [80, 50],
                iconAnchor: [40, 25]
            }}) 
        }}).addTo(map);
        
        // Draw a circle indicating area of effect
        L.circle({current_state['coords']}, {{
            color: '#3b82f6',
            fillColor: '#3b82f6',
            fillOpacity: 0.1,
            radius: 150000,
            weight: 2,
            dashArray: '5, 10'
        }}).addTo(map);
    </script>
</body>
</html>
"""

# 8. Render UI (Classic Flow)
# Sidebar
with st.sidebar:
    st.markdown("<h1 style='color:#6366f1; letter-spacing:2px; font-weight:800; font-size:2rem;'>LORI</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("""
        <div style='display:flex; flex-direction:column; gap:1.5rem; font-size:1.1rem; color:#94a3b8;'>
            <div style='color:#fff; font-weight:600;'>🏠 Dashboard</div>
            <div>📈 Analytics</div>
            <div>⚙️ Settings</div>
            <div>👤 Profile</div>
        </div>
    """, unsafe_allow_html=True)

# Main Container
st.markdown("<div class='header-title'>Environmental Dashboard 2025</div>", unsafe_allow_html=True)
st.markdown("<div class='header-sub'>Analyze environmental trends for Indian cities in 2025</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
# Inputs
i1, i2, i3, i4 = st.columns(4)
with i1:
    sel_city = st.selectbox("Select City", options=data['City'].unique(), index=list(data['City'].unique()).index(st.session_state.city))
with i2:
    sel_month = st.selectbox("Select Month", options=month_options, index=month_options.index(st.session_state.month_full))
with i3:
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    if st.button("Show Results", use_container_width=True):
        st.session_state.city = sel_city
        st.session_state.month_full = sel_month
        st.rerun()

if sel_city != st.session_state.city or sel_month != st.session_state.month_full:
    st.session_state.city = sel_city
    st.session_state.month_full = sel_month
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Map Section
st.markdown("### Region Coverage")
m_left, m_right = st.columns([3, 1])
with m_left:
    st.markdown("<div class='card' style='padding:0;'>", unsafe_allow_html=True)
    components.html(leaflet_html, height=450)
    st.markdown("</div>", unsafe_allow_html=True)
with m_right:
    st.markdown(f"""
    <div class='card'>
        <h4 style="color:#6366f1; font-size:1rem; margin-top:0; margin-bottom:1rem; padding-bottom:1rem; border-bottom:1px solid rgba(255,255,255,0.1);">GEO METADATA</h4>
        <div class="meta-item">
            <div class="meta-label">State</div>
            <div class="meta-value">{state_mapping[city]['name']}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Coordinates</div>
            <div class="meta-value">{state_mapping[city]['coords'][0]:.4f},<br>{state_mapping[city]['coords'][1]:.4f}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Data Points</div>
            <div class="meta-value">12 Months Selected</div>
        </div>
        <div class="meta-item" style="margin-top:2rem;">
            <div class="meta-label">Avg Temp ({month_abbr})</div>
            <div class="meta-value" style="color:#f43f5e;">{month_data['Avg_Temp']}°C</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Graphs Section
st.markdown("### Monthly Trends & Comparison")
g_left, g_right = st.columns(2)
with g_left:
    st.markdown("<div class='card'><h4 style='margin-top:0; color:#cbd5e1;'>Thermal Trends</h4>", unsafe_allow_html=True)
    st.plotly_chart(fig_temp, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)
with g_right:
    st.markdown("<div class='card'><h4 style='margin-top:0; color:#cbd5e1;'>AQI Status</h4>", unsafe_allow_html=True)
    st.plotly_chart(fig_aqi, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# Insights Section
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Regional Insights")
st.markdown("<div class='card'>", unsafe_allow_html=True)
in1, in2, in3, in4 = st.columns(4)
stats = [
    ("AQI", month_data['AQI']), 
    ("HUMIDITY", f"{month_data['Humidity']}%"),
    ("WIND", "12 km/h"), 
    ("PRESSURE", "1012 hPa")
]
for i, col in enumerate([in1, in2, in3, in4]):
    with col:
        border_right = "border-right: 1px solid rgba(255,255,255,0.1);" if i < 3 else ""
        st.markdown(f"""
        <div style='text-align:center; {border_right}'>
            <div style='color:#94a3b8;font-size:0.8rem;letter-spacing:1px;margin-bottom:0.5rem;'>{stats[i][0]}</div>
            <div style='font-size:1.8rem;font-weight:800;color:#f8fafc;'>{stats[i][1]}</div>
        </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
