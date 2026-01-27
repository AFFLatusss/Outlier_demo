# outlier_page.py
import streamlit as st
from outlier_tabs.filter_outlier import filter_outlier
from outlier_tabs.search_outlier import search_outlier

st.title("📊 离散点筛选")

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




filter_outlier, search_outlier = st.tabs(["filter_outlier", "search_outlier"])

with filter_outlier:
    filter_outlier()

with search_outlier:
    search_outlier()
