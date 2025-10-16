import streamlit as st
import pandas as pd
import numpy as np
from utils import huafeng, liandong, spea

# ===========================================================================================

st.title('Outlier Detection DEMO')

option = st.selectbox(
    "选择测试设备",
    ("FT-001", "FT-002", "FT-003","FT-006"),
)

st.write("You selected:", option)

if option:

    uploaded_files = st.file_uploader(
        "上传测试数据", type="csv"
    )

    if uploaded_files:
        with st.spinner("处理中...", show_time=True):
            match option:
                case "FT-001":
                    df = spea.read_csv(uploaded_files)
                case "FT-002":
                    df = spea.read_csv(uploaded_files)
                case "FT-003":
                    df = liandong.read_csv(uploaded_files)
                case "FT-006":
                    df = huafeng.read_csv(uploaded_files)
            
            if df is None:
                st.error('读取文件', icon="🚨")
            else:
                st.write(df)
