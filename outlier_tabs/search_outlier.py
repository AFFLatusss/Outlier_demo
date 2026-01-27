# tab2.py
import streamlit as st

def search_render():

    # -------------------------------------------------
    # Searching Outlier 
    # -------------------------------------------------

    with st.form("search_outlier_form"):
        col1, col2 = st.columns([1, 1])

        with col1:
            circulate_no = st.text_input("流转单号：", max_chars=20)
            module_id = st.text_input("模块编号：", max_chars=100)

        with col2:

            machine_id = st.text_input("测试设备：", max_chars=100)
            product_name = st.text_input("产品型号：", max_chars=100)
        submit = st.form_submit_button("查询")

        if submit:
            if not circulate_no and not module_id and not machine_id and not product_name:
                st.error("请输入流转单号、模块编号、测试设备或产品型号", icon="🚨")
                return
            
            st.write(f"查询参数：流转单号={circulate_no}, 模块编号={module_id}, 测试设备={machine_id}, 产品型号={product_name}")    
