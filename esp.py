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

TIME_OPTIONS = {
    "30M": "-30m", "1H": "-1h", "3H": "-3h", 
    "5H": "-5h", "12H": "-12h", "24H": "-24h"
}

COLOR_MAP = {
    "red": "#FF0000",
    "green": "#00FF00",
    "yellow": "#FFFF00",
    "count": "#0000FF"
}

# Machine ID to MAC Mapping
MACHINE_MAP = {
    "DA-08": "AC:A7:04:13:6B:60",
    "AGT-001": "AC:A7:04:29:82:94",
}

st.set_page_config(layout="wide")
st.title("三色灯数据监控看板")

db = InfluxManager(**INFLUX_CONFIG)

# --- Sidebar / Controls ---
with st.sidebar:
    st.header("查询配置")
    
    # User selects the Machine ID (Key)
    selected_machine_id = st.selectbox(
        "选择设备",
        options=list(MACHINE_MAP.keys()),
        index=0,
    )

    # Get the corresponding MAC address (Value) for the database query
    target_mac = MACHINE_MAP[selected_machine_id]

    selected_label = st.selectbox(
        "选择时间范围",
        options=list(TIME_OPTIONS.keys()),
        index=1 
    )
    
    flux_range = TIME_OPTIONS[selected_label]
    fetch_clicked = st.button("获取数据", type="primary", use_container_width=True)

# --- Data Fetching Logic ---
if fetch_clicked:
    with st.spinner(f"正在获取 {selected_machine_id} 的数据..."):
        # CRITICAL: We pass the MAC address to the DB, not the Machine ID
        df = db.get_high_freq_data(mac_address=target_mac, range_str=flux_range)
        
        # Store data and the Name for the UI
        st.session_state['df'] = df
        st.session_state['current_display_name'] = selected_machine_id
        st.session_state['last_range'] = selected_label

# --- Visualization ---
if 'df' in st.session_state and not st.session_state['df'].empty:
    df = st.session_state['df']
    
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
            # Use the Display Name in the title
            title=f"设备: {st.session_state.get('current_display_name')} - 历史趋势 ({st.session_state.get('last_range')})",
            color_discrete_map=COLOR_MAP,
            render_mode="webgl"
        )
        
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(
            height=700,
            hovermode="x unified",
            legend_title="指标"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("请选择至少一个指标。")

elif 'df' in st.session_state:
    st.warning(f"设备 {st.session_state.get('current_display_name')} 在所选时间内无数据。")