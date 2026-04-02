import streamlit as st
import plotly.express as px
from influx.database import InfluxManager 

# --- Configuration ---
INFLUX_CONFIG = {
    "url": "http://10.168.0.51:8086",
    "token": "admin111.",
    "org": "docs",
    "bucket": "mqtt"
}

# Mapping user labels to InfluxDB Flux range strings
TIME_OPTIONS = {
    "30M": "-30m",
    "1H": "-1h",
    "3H": "-3h",
    "5H": "-5h",
    "12H": "-12h",
    "24H": "-24h"
}

COLOR_MAP = {
    "red": "#FF0000",
    "green": "#00FF00",
    "yellow": "#FFFF00",
    "count": "#0000FF"
}

st.set_page_config(layout="wide")
st.title("三色灯数据样例")

db = InfluxManager(**INFLUX_CONFIG)

# --- Sidebar / Controls ---
with st.sidebar:
    st.header("查询配置")
    
    mac_address = st.selectbox(
        "选择MAC地址",
        ("AC:A7:04:13:6B:60", "AC:A7:04:29:82:94"),
        index=0,
    )

    # New Time Range Selector
    selected_label = st.selectbox(
        "选择时间范围",
        options=list(TIME_OPTIONS.keys()),
        index=1 # Default to 1 Hour
    )
    
    # Convert label to Flux string (e.g., "1 Hour" -> "-1h")
    flux_range = TIME_OPTIONS[selected_label]

    fetch_clicked = st.button("获取数据", type="primary", use_container_width=True)

# --- Data Fetching Logic ---
if fetch_clicked:
    with st.spinner(f"正在获取 {selected_label} 的数据..."):
        # Pass the dynamic flux_range to your database function
        df = db.get_high_freq_data(mac_address=mac_address, range_str=flux_range)
        st.session_state['df'] = df
        st.session_state['current_mac'] = mac_address

# --- Visualization ---
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    
    # Explicitly show only your 4 target columns
    target_cols = ["red", "green", "yellow", "count"]
    available_cols = [c for c in df.columns if c in target_cols]

    selected_metrics = st.multiselect(
        "选择要显示的数据", 
        options=available_cols, 
        default=available_cols 
    )

    if selected_metrics:
        fig = px.line(
            df, 
            x='_time', 
            y=selected_metrics, 
            title=f"MAC: {st.session_state.get('current_mac')} - 历史趋势 ({selected_label})",
            color_discrete_map=COLOR_MAP,
            render_mode="webgl"
        )
        
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(
            height=700,
            hovermode="x unified",
            legend_title="指标",
            # Optional: makes the lines "step" rather than "slope"
            # line_shape='hv' 
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("请选择至少一个指标。")

elif 'df' in st.session_state:
    st.warning("所选时间范围内无数据。")