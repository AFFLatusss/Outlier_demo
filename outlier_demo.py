# outlier_page.py
import streamlit as st
from outlier_tabs import filter_outlier, search_outlier

st.title("📊 离散点筛选")
# st.set_page_config(page_title="离散点筛选", layout="wide")
st.markdown("""
    <style>
    /* Target the individual tab buttons */
    button[data-baseweb="tab"] {
        margin-right: 30px !important; /* Increase space between tabs */
        padding-left: 20px !important;  /* Add internal spacing for a bigger click area */
        padding-right: 20px !important;
        gap: 10px !important;
    }
    
    /* Optional: Make the text bigger */
    button[data-baseweb="tab"] p {
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)




filter_tab, search_tab = st.tabs(["离散点筛选/上传", "离散点查询"])

with filter_tab:
    filter_outlier.filter_outlier() 


with search_tab:
    search_outlier.search_render()

