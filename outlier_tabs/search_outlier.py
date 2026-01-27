import requests
import streamlit as st
import pandas as pd

def search_render():

    # 1. 初始化 Session State 存储查询结果
    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    # -------------------------------------------------
    # Searching Outlier Form
    # -------------------------------------------------
    with st.form("search_outlier_form"):
        col1, col2 = st.columns(2)
        with col1:
            circulate_no = st.text_input("流转单号：", max_chars=20)
            module_id = st.text_input("模块编号：", max_chars=100)
        with col2:
            machine_id = st.text_input("测试设备：", max_chars=100)
            product_name = st.text_input("产品型号：", max_chars=100)
        
        submit = st.form_submit_button("查询", type="primary")

        if submit:
            if not any([circulate_no, module_id, machine_id, product_name]):
                st.error("请输入至少一个查询条件", icon="🚨")
                return
            
            search_params = {
                "circulate_no": circulate_no.strip(),
                "module_id": module_id.strip(),
                "machine_id": machine_id.strip(),
                "product_name": product_name.strip(),
            }   

            try:
                with st.spinner("正在从 MES 数据库检索..."):
                    response = requests.get(
                        "http://127.0.0.1:8000/outlier/get_outlier_info",
                        params=search_params,
                        timeout=15,
                    )
                    
                    if response.ok:
                        result = response.json()
                        # 重点：将数据存入 session_state
                        st.session_state.search_results = result.get("outlier_data", [])
                        
                        if not st.session_state.search_results:
                            st.warning("未找到匹配的数据")
                        else:
                            st.toast("数据加载成功！")
                    else:
                        error_msg = response.json().get("detail", "未知错误")
                        st.error(f"查询失败: {error_msg}")
                        st.session_state.search_results = None

            except requests.exceptions.RequestException as e:
                st.error(f"API 连接失败：{e}")
                st.session_state.search_results = None

    # -------------------------------------------------
    # 2. 在表单外部显示结果
    # -------------------------------------------------
    # 只有当 session_state 里面有数据（不是 None 且不为空列表）时才显示
    if st.session_state.search_results:
        outlier_df = pd.DataFrame(st.session_state.search_results).rename(columns={
            "serial_number": "模块编码",
            "circulate_no": "流转单号",
            "machine": "测试设备",
            "product": "产品型号",
            "upload_timestamp": "上传时间",
            "uploaded_by": "上传用户",
            "file_name": "文件名称",
        })
        
        st.divider()
        st.success(f"✅ 找到 {len(outlier_df)} 条记录", icon="📊")
        
        # 使用 dataframe 展示，并允许下载
        st.dataframe(outlier_df, use_container_width=True)
        
        # 额外：加一个清空结果的按钮
        if st.button("清除查询结果"):
            st.session_state.search_results = None
            st.rerun()