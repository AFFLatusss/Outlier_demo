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
# Count Chart
# --------------------------------------------------------

count_fig = px.line(
    df,
    x="_time",
    y="count",
    markers=False
)

count_fig.update_layout(
    title="Count Signal",
    height=350,
    hovermode="x unified"
)

count_fig.update_traces(
    line=dict(width=2)
)

st.plotly_chart(
    count_fig,
    use_container_width=True
)

# --------------------------------------------------------
# Timeline
# --------------------------------------------------------

timeline = []

for signal in ["green", "yellow", "red"]:
    timeline.extend(build_intervals(df, signal))

timeline_df = pd.DataFrame(timeline)

if not timeline_df.empty:

    gantt = px.timeline(
        timeline_df,
        x_start="Start",
        x_end="Finish",
        y="Signal",
        color="Signal",
        color_discrete_map=LIGHT_COLOR
    )

    gantt.update_yaxes(
        autorange="reversed"
    )

    gantt.update_layout(
        title="Machine Light Timeline",
        height=300,
        showlegend=False,
        hovermode="x"
    )

    st.plotly_chart(
        gantt,
        use_container_width=True
    )

# --------------------------------------------------------
# Statistics
# --------------------------------------------------------

st.subheader("Statistics")

duration = (
    df["_time"].max() -
    df["_time"].min()
).total_seconds()

cols = st.columns(4)

for i, signal in enumerate(["green", "yellow", "red"]):

    pct = round(df[signal].eq(1).mean() * 100, 2)

    cols[i].metric(
        f"{signal.capitalize()} %",
        f"{pct}%"
    )

disconnect = round(
    (
        (df[["red", "yellow", "green"]] == -1)
        .all(axis=1)
        .mean()
    ) * 100,
    2
)

cols[3].metric(
    "Disconnect %",
    f"{disconnect}%"
)