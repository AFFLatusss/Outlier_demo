import streamlit as st
import pandas as pd
import chardet
from io import StringIO, BytesIO
from utils.plot import plot_scatter

# --- Configuration and Title ---
# st.set_page_config(layout="wide")
st.title("📄 散点图")

uploaded_files = st.file_uploader("📂 上传测试数据 (xlsx 格式)(请勿加密)", type="xlsx")

if not uploaded_files:
    st.info("等待上传 xlsx 测试数据。")
    st.stop()

df = pd.read_excel(uploaded_files)

columns_options = list(df.iloc[:,6:].columns)

options = st.multiselect(
    "选择列名：",
    columns_options,
    default=None,
)

for column in options:
    plot_scatter(df[column])