import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from influx.database import InfluxManager

# --- Config ---
INFLUX_CONFIG = {"url": "http://10.168.0.51:8086", "token": "admin111.", "org": "docs", "bucket": "mqtt"}
COLOR_MAP = {"red": "#FF4B4B", "green": "#00CC96", "yellow": "#FACA2B", "count": "#636EFA"}
TIME_OPTIONS = {"30M": "-30m", "1H": "-1h", "3H": "-3h", "5H": "-5h", "12H": "-12h", "24H": "-24h"}

st.set_page_config(layout="wide")
st.title("🚦 设备状态看板 (Timeline + Trend)")

db = InfluxManager(**INFLUX_CONFIG)

with st.sidebar:
    mac_address = st.selectbox("选择MAC地址", ("AC:A7:04:13:6B:60", "AC:A7:04:29:82:94"))
    selected_label = st.selectbox("选择时间范围", options=list(TIME_OPTIONS.keys()), index=1)
    fetch_clicked = st.button("获取数据", type="primary", use_container_width=True)

if fetch_clicked:
    df = db.get_high_freq_data(mac_address=mac_address, range_str=TIME_OPTIONS[selected_label])
    st.session_state['df'] = df

# --- Visualization Logic ---
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    
    # Define which metrics go to which style
    status_cols = ["red", "green", "yellow"]
    trend_cols = ["count"]
    
    # Filter columns actually present in the data
    active_status = [c for c in status_cols if c in df.columns]
    active_trend = [c for c in trend_cols if c in df.columns]
    total_rows = len(active_status) + len(active_trend)

    # Create subplots
    fig = make_subplots(
        rows=total_rows, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03,
        row_heights=[0.15] * len(active_status) + [0.55] * len(active_trend),
        subplot_titles=active_status + active_trend
    )

    # 1. Add STATUS TIMELINES (The "Barcode" look)
    # 1. Add STATUS TIMELINES (The "Barcode" look)
    for i, col in enumerate(active_status):
        fig.add_trace(
            go.Heatmap(
                x=df['_time'],
                y=[col],
                # Explicitly wrap the values in a list to create a 2D array [ [val1, val2...] ]
                z=[df[col].values.tolist()], 
                # Fix the scale so 0 is ALWAYS mapped to the first color 
                # and 1 is ALWAYS mapped to the second color
                zmin=0,
                zmax=1,
                colorscale=[
                    [0, "#E5ECF6"], # Grey/Blue for OFF (0)
                    [1, COLOR_MAP[col]] # Specific color for ON (1)
                ],
                showscale=False,
                hoverongaps=False,
                hovertemplate="时间: %{x}<br>状态: %{z}<extra></extra>"
            ),
            row=i+1, col=1
        )
    # 2. Add COUNT TREND (The Line Graph)
    for i, col in enumerate(active_trend):
        row_idx = len(active_status) + i + 1
        fig.add_trace(
            go.Scatter(
                x=df['_time'], y=df[col],
                name=col,
                line=dict(color=COLOR_MAP[col], width=2),
                fill='tozeroy', # Fills area under the count for better visibility
                mode='lines'
            ),
            row=row_idx, col=1
        )

    # Layout Tuning
    fig.update_layout(
        height=300 + (150 * total_rows),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    
    # Single Range Slider at the bottom
    fig.update_xaxes(rangeslider_visible=True, row=total_rows, col=1)
    
    # Remove Y-axis labels for heatmaps to keep it clean
    for i in range(1, len(active_status) + 1):
        fig.update_yaxes(showticklabels=False, row=i, col=1)

    st.plotly_chart(fig, use_container_width=True)

elif 'df' in st.session_state:
    st.warning("所选范围内无有效数据。")