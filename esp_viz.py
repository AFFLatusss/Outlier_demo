import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from influx.database import InfluxManager

# --------------------------------------------------------
# Configuration
# --------------------------------------------------------

INFLUX_CONFIG = {
    "url": "http://10.168.0.51:8086",
    "token": "admin111.",
    "org": "docs",
    "bucket": "mqtt"
}

TIME_OPTIONS = {
    "30M": "-30m",
    "1H": "-1h",
    "3H": "-3h",
    "5H": "-5h",
    "12H": "-12h",
    "24H": "-24h"
}

MACHINE_MAP = {
    "DA-08": "AC:A7:04:13:1D:DC",
    "DA-06": "AC:A7:04:13:6B:60",
    "AGT-001": "AC:A7:04:29:82:94",
    "PRINT-02":"AC:A7:04:13:FD:EC",
    "REFLOW-01":"E8:F6:0A:8A:40:04",
    "FT-001":"AC:A7:04:E2:69:6C",
    "FT-002":"AC:A7:04:E2:4B:04",
    "FT-003":"AC:A7:04:E2:46:8C",
    "FT-005":"AC:A7:04:E2:53:38",
    "FT-006":"AC:A7:04:E2:70:50",
    "FT-010":"AC:A7:04:E2:46:C0",
    "FT-011":"AC:A7:04:E1:0B:2C",
    "FT-013":"E8:F6:0A:8A:74:B4",
    "LZ-K-036":"AC:A7:04:E0:52:24",
    "KD-01":"AC:A7:04:E2:49:58",
    "WB-12":"AC:A7:04:E0:F9:4C",
    "CLN-01":"AC:A7:04:E0:51:78",
    "CLN-02":"AC:A7:04:E0:F9:58",
    "APLP-01":"E8:F6:0A:8A:76:5C",
    "APLP-02":"AC:A7:04:E2:6F:78",
    "APLP-03":"AC:A7:04:E2:56:DC",
}

LIGHT_COLOR = {
    "Red": "#ff4d4f",
    "Yellow": "#fadb14",
    "Green": "#52c41a"
}

# --------------------------------------------------------
# Page
# --------------------------------------------------------

st.set_page_config(layout="wide")
st.title("🚦 Machine Signal Dashboard")

db = InfluxManager(**INFLUX_CONFIG)

# --------------------------------------------------------
# Sidebar
# --------------------------------------------------------

with st.sidebar:

    st.header("Search")

    machine = st.selectbox(
        "Machine",
        list(MACHINE_MAP.keys())
    )

    time_label = st.selectbox(
        "Time Range",
        list(TIME_OPTIONS.keys()),
        index=1
    )

    if st.button("Fetch Data", use_container_width=True):

        mac = MACHINE_MAP[machine]

        with st.spinner("Loading..."):

            df = db.get_high_freq_data(
                mac_address=mac,
                range_str=TIME_OPTIONS[time_label]
            )

            st.session_state.df = df
            st.session_state.machine = machine
            st.session_state.time = time_label

# --------------------------------------------------------
# Build Timeline
# --------------------------------------------------------

def build_intervals(df, signal):

    df = df.sort_values("_time").reset_index(drop=True)

    intervals = []

    start = None

    for i in range(len(df)):

        value = df.loc[i, signal]

        if value == 1 and start is None:
            start = df.loc[i, "_time"]

        elif value != 1 and start is not None:

            intervals.append({
                "Signal": signal.capitalize(),
                "Start": start,
                "Finish": df.loc[i, "_time"]
            })

            start = None

    if start is not None:

        intervals.append({
            "Signal": signal.capitalize(),
            "Start": start,
            "Finish": df.iloc[-1]["_time"]
        })

    return intervals

# --------------------------------------------------------
# Visualization
# --------------------------------------------------------

if "df" not in st.session_state:
    st.info("Select a machine and click Fetch Data.")
    st.stop()

df = st.session_state.df

if df.empty:
    st.warning("No data found.")
    st.stop()

df = df.sort_values("_time")

# --------------------------------------------------------
# Current Status
# --------------------------------------------------------

latest = df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🔴 Red",
        "ON" if latest["red"] else "OFF"
    )

with c2:
    st.metric(
        "🟡 Yellow",
        "ON" if latest["yellow"] else "OFF"
    )

with c3:
    st.metric(
        "🟢 Green",
        "ON" if latest["green"] else "OFF"
    )

with c4:
    st.metric(
        "Count",
        int(latest["count"])
    )

st.divider()
# --------------------------------------------------------
# Build Timeline Data
# --------------------------------------------------------
timeline = []
for signal in ["green", "yellow", "red"]:
    timeline.extend(build_intervals(df, signal))

timeline_df = pd.DataFrame(timeline)
# --------------------------------------------------------
# Stacked Visualization (Dedicated Lanes / Logic Analyzer View)
# --------------------------------------------------------

# 1. 创建 4 行的子图，共享 X 轴
fig = make_subplots(
    rows=4, cols=1, 
    shared_xaxes=True,
    vertical_spacing=0.03, # 缩小行间距，让它们看起来像一个整体的仪器屏幕
    row_heights=[0.4, 0.2, 0.2, 0.2], # 分配高度比例
    subplot_titles=("Machine Signals & Count", "", "", "") # 只在最上方留一个标题
)

# 2. 将 Count 曲线放入第 1 行
fig.add_trace(
    go.Scatter(
        x=df["_time"],
        y=df["count"],
        mode="lines",
        name="Count",
        line=dict(width=2, color="#1f77b4"),
        hovertemplate="Time: %{x}<br>Count: %{y}<extra></extra>"
    ),
    row=1, col=1
)
fig.update_yaxes(title_text="Count", row=1, col=1)

# 3. 将每个灯分配到专属的行 (第 2, 3, 4 行)
row_idx = 2
for light, color in LIGHT_COLOR.items():
    col_name = light.lower()
    
    fig.add_trace(
        go.Scatter(
            x=df["_time"],
            y=df[col_name],
            mode="lines",
            name=light,
            line_shape="hv",  # 保持阶梯图表
            line=dict(color=color, width=2),
            fill="tozeroy",   # 向下填充颜色
            opacity=0.8,      # 不再担心重叠，可以把透明度调高一点让颜色更鲜艳
            hovertemplate=f"<b>{light}</b><br>Time: %{{x}}<br>Status: %{{y}}<extra></extra>"
        ),
        row=row_idx, col=1
    )
    
    # 锁定该灯专属 Y 轴的范围，并在左侧加上文字标签
    fig.update_yaxes(
        title_text=light,  # 在 Y 轴左侧显示 "Red", "Yellow", "Green"
        range=[-0.1, 1.1], 
        tickvals=[0, 1], 
        ticktext=["OFF", "ON"], 
        row=row_idx, col=1
    )
    
    row_idx += 1

# 4. 全局排版调整
fig.update_layout(
    height=650, # 稍微增加整体高度，防止 4 行显得拥挤
    hovermode="x unified", # 核心！鼠标悬停时，一条竖线会贯穿 4 行，同时显示所有状态！
    margin=dict(l=20, r=20, t=40, b=20),
    showlegend=False # 因为 Y 轴已经有了标题，图例显得多余，直接隐藏掉让图表更宽
)

# 渲染到 Streamlit
st.plotly_chart(fig, use_container_width=True)