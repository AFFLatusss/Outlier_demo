import streamlit as st

outlier_page = st.Page("outlier_demo.py", title="离散点筛选")
merge_csv_page = st.Page("merge_csv.py", title="Merge CSV")
bpm_resign_search = st.Page("bpm_resign_search.py", title="BPM指定账号查询")
ip_addr_check = st.Page("ip_addr_check.py", title="IP地址查询")
scatter_plot_page = st.Page("scatter_plot.py", title="散点图")



pg = st.navigation([outlier_page, merge_csv_page,scatter_plot_page, bpm_resign_search])
# st.set_page_config(page_title="Data manager")
pg.run()