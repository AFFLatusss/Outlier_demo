import streamlit as st
import pandas as pd
import numpy as np
from utils import huafeng, liandong, spea

# ===========================================================================================

st.title('离散点/并联检测 DEMO')

option = st.selectbox(
    "选择测试设备",
    ("FT-001", "FT-002", "FT-003","FT-006"),
    index=None,
    placeholder="设备",
)

selection = st.segmented_control(
    "筛选：", ["离散点","并联"], selection_mode="multi"
)
# st.markdown(f"Your selected options: {selection}.")

if option:
    if selection:
        uploaded_files = st.file_uploader(
            "上传测试数据", type="csv"
        )

        if uploaded_files:
            with st.spinner("处理中...", show_time=True):
                match option:       
                    case "FT-001":
                        df, err = spea.read_csv(uploaded_files)
                    case "FT-002":
                        df, err = spea.read_csv(uploaded_files)
                    case "FT-003":
                        df, err = liandong.read_csv(uploaded_files)
                    case "FT-006":
                        df, err = huafeng.read_csv(uploaded_files)
                
                if err:
                    st.error(err, icon="🚨")
                else:
                    st.write(df)
                    st.badge("Success", icon=":material/check:", color="green")
                    st.write(f"共找到{df.shape[0]}条离散点")
    else:
        st.error("请先选择筛选项", icon="🚨")
else:
    st.error("请先选择测试设备", icon="🚨")
