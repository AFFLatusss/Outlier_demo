import streamlit as st

outlier_page = st.Page("outlier_demo.py", title="离散点DEMO")
merge_csv_page = st.Page("merge_csv.py", title="Merge CSV")
bpm_resign_search = st.Page("bpm_resign_search.py", title="BPM指定账号查询")
ip_addr_check = st.Page("ip_addr_check.py", title="IP地址查询")
pg = st.navigation([outlier_page, merge_csv_page, bpm_resign_search, ip_addr_check])
st.set_page_config(page_title="Data manager")
pg.run()