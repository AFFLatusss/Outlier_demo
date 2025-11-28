import streamlit as st

outlier_page = st.Page("pages\outlier_demo.py", title="离散点DEMO")
merge_csv_page = st.Page("pages\merge_csv.py", title="Merge CSV")

pg = st.navigation([outlier_page, merge_csv_page])
st.set_page_config(page_title="Data manager")
pg.run()