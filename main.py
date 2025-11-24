import streamlit as st
import pandas as pd
import numpy as np
from utils import huafeng, liandong, spea

st.set_page_config(page_title="离散点检测 DEMO")
st.title("📊 离散点检测 DEMO")

# -----------------------------
# Step 1: Select device
# -----------------------------
option = st.selectbox(
    "选择测试设备",
    ("FT-001", "FT-002", "FT-003", "FT-006"),
    index=None,
    placeholder="请选择设备...",
)

if not option:
    st.error("请先选择测试设备", icon="🚨")
    st.stop()
elif option == "FT-001" or option == "FT-002":
    st.warning("SPEA 设备暂不支持离散点检测。", icon="⚠️")
    st.stop()

# -----------------------------
# Step 2: Select mode
# -----------------------------
# selection = st.segmented_control("筛选：", ["离散点", "并联"], selection_mode="multi")
# if not selection:
#     st.error("请先选择筛选项", icon="🚨")
#     st.stop()

# -----------------------------
# Step 3: Upload file
# -----------------------------
uploaded_files = st.file_uploader("📂 上传测试数据 (CSV 格式)", type="csv")
if not uploaded_files:
    st.info("等待上传 CSV 测试数据。")
    st.stop()

# -----------------------------
# Step 4: Process file
# -----------------------------
readers = {
    "FT-001": spea.read_csv,
    "FT-002": spea.read_csv,
    "FT-003": liandong.read_csv,
    "FT-006": huafeng.read_csv,
}

reader_func = readers.get(option)
if not reader_func:
    st.error("未知设备类型，请检查配置。", icon="🚨")
    st.stop()

with st.spinner("处理中，请稍候..."):
    df, err = reader_func(uploaded_files)

if err:
    st.error(err, icon="🚨")
    st.stop()

# -----------------------------
# Step 5: Show results
# -----------------------------
if df is None or df.empty:
    st.warning("没有找到任何离散点记录。")
else:
    st.success(f"✅ 成功找到 {df.shape[0]} 条离散点")
    st.dataframe(df, use_container_width=True)
