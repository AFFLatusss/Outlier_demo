# tab1.py
import streamlit as st
import pandas as pd
import requests

from utils import huafeng, liandong, spea

def filter_outlier():
    # -------------------------------------------------
    # Step 1: Select device
    # -------------------------------------------------
    option = st.selectbox(
        "选择测试设备",
        ("FT-001", "FT-002", "FT-003", "FT-006"),
        index=None,
        placeholder="请选择设备...",
    )

    if not option:
        st.error("请先选择测试设备", icon="🚨")
        st.stop()
    # elif option == "FT-001" or option == "FT-002":
    #     st.warning("SPEA 设备暂不支持离散点检测。", icon="⚠️")
    #     st.stop()

    # -----------------------------
    # Step 2: Select mode
    # -----------------------------
    # selection = st.segmented_control("筛选：", ["离散点", "并联"], selection_mode="multi")
    # if not selection:
    #     st.error("请先选择筛选项", icon="🚨")
    #     st.stop()

    # -------------------------------------------------
    # Step 2: Upload file
    # -------------------------------------------------
    uploader_key = f"uploader_{option}"

    if option == "FT-006":
        uploaded_files = st.file_uploader(
            "📂 上传测试数据 (CSV 格式)",
            type=["csv"],
            key=uploader_key,
        )
    else:
        uploaded_files = st.file_uploader(
            "📂 上传测试数据 (CSV / XLSX 格式)",
            type=["csv", "xlsx"],
            key=uploader_key,
        )

    if not uploaded_files:
        st.info("等待上传 CSV / XLSX 测试数据。")
        st.stop()

    # -------------------------------------------------
    # Step 3: Process file
    # -------------------------------------------------
    readers = {
        "FT-001": spea.read_csv,
        "FT-002": spea.read_csv,
        "FT-003": liandong.read_csv,
        "FT-006": huafeng.read_csv,
    }

    reader_func = readers.get(option)
    if not reader_func:
        st.error("未知设备类型，请检查配置。", icon="🚨")
        st.stop()

    try:
        with st.spinner("处理中，请稍候..."):
        
            result = reader_func(uploaded_files, type="modules")
            # st.write(result)
            # if result["error"]:
            #     raise Exception(result["error"])
    except Exception as e:
        st.error(str(e), icon="🚨")
        st.stop()

    # -------------------------------------------------
    # Step 4: Show results
    # -------------------------------------------------
    if result["outlier"] is None or result["outlier"].empty:
        st.warning("没有找到任何离散点记录。")
        st.stop()

    outlier_count = result["outlier"].shape[0]
    st.success(f"✅ 成功找到 {outlier_count} 条离散点")
    st.dataframe(result["outlier"], use_container_width=True)

    # -------------------------------------------------
    # Helper: DataFrame → API Payload
    # -------------------------------------------------
    def df_to_payload(df: pd.DataFrame,circulate_no:str, product_name: str, employee_id: str, password: str, device: str) -> dict:
        return {
            "circulate_no": circulate_no,
            "product_name": product_name,
            "employee_id": employee_id,
            "password": password,
            "device": device,
            "records": df.tolist(),
            "file_name": uploaded_files.name,

        }

    # -------------------------------------------------
    # Submit Dialog (Modal)
    # -------------------------------------------------
    @st.dialog("📤 提交离散点数据")
    def submit_dialog(df: pd.DataFrame, circulate_no: str, product_name: str, device: str):
        st.write("请确认以下信息：")
        st.write(f":orange[产品名称]：{product_name}")
        st.write(f":blue[流转单号]：{circulate_no}")
        st.write(f":green[离散点数量]：{df.shape[0]}")
        with st.form("submit_form"):
            
            employee_id = st.text_input(
                "用户名",
                placeholder="请输入用户名",
            )
            password = st.text_input(
                "密码",
                placeholder="请输入密码",
                type="password",
            )

            submit = st.form_submit_button("✅ 确认提交")
            
            if submit:
                if not employee_id.strip() or not password.strip():
                    st.error("用户名和密码不能为空")
                    return
                

                payload = df_to_payload(df, circulate_no, product_name, employee_id, password, device)

                st.write(payload)
                try:
                        response = requests.post(
                            "http://127.0.0.1:8000/outlier/insert_outliers",
                            json=payload,
                            timeout=15,
                        )
                        if response.ok:
                            st.success("🎉 数据提交成功！")
                        else:
                            error_msg = response.json()["detail"]
                            st.error(
                                f"用户认证失败\n"
                                f":{error_msg}"
                            )
                            return
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"API 调用失败：{e}")

    # -------------------------------------------------
    # Trigger Button
    # -------------------------------------------------
    st.divider()

    if st.button("📤 提交结果到MES", type="primary"):
        submit_dialog(result["outlier"], result["circulate_no"], result["product_name"], option)