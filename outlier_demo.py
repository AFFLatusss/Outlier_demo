import streamlit as st
import pandas as pd
import requests

from utils import huafeng, liandong, spea

# -------------------------------------------------
# Page Title
# -------------------------------------------------
st.title("📊 离散点筛选")

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

with st.spinner("处理中，请稍候..."):
    try:
        df, err = reader_func(uploaded_files, type="modules")
        if err:
            raise Exception(err)
    except ValueError as e:
        st.error(str(e), icon="🚨")
        st.stop()

# -------------------------------------------------
# Step 4: Show results
# -------------------------------------------------
if df is None or df.empty:
    st.warning("没有找到任何离散点记录。")
    st.stop()

st.success(f"✅ 成功找到 {df.shape[0]} 条离散点")
st.dataframe(df, use_container_width=True)

# # -------------------------------------------------
# # Helper: DataFrame → API Payload
# # -------------------------------------------------
# def df_to_payload(df: pd.DataFrame, employee_id: str, device: str) -> dict:
#     return {
#         "employee_id": employee_id,
#         "device": device,
#         "row_count": len(df),
#         "records": df.to_dict(orient="records"),
#     }

# # -------------------------------------------------
# # Submit Dialog (Modal)
# # -------------------------------------------------
# @st.dialog("📤 提交离散点数据")
# def submit_dialog(df: pd.DataFrame, device: str):
#     with st.form("submit_form"):
#         employee_id = st.text_input(
#             "员工 ID",
#             placeholder="请输入员工工号",
#         )

#         submit = st.form_submit_button("✅ 确认提交")

#         if submit:
#             if not employee_id.strip():
#                 st.error("员工 ID 不能为空")
#                 return

#             payload = df_to_payload(df, employee_id.strip(), device)

#             with st.spinner("正在上传数据到服务器..."):
#                 try:
#                     response = requests.post(
#                         "https://your-api-endpoint/upload-outlier",
#                         json=payload,
#                         timeout=15,
#                     )

#                     if response.ok:
#                         st.success("🎉 数据提交成功！")
#                     else:
#                         st.error(
#                             f"提交失败\n"
#                             f"状态码：{response.status_code}\n"
#                             f"返回内容：{response.text}"
#                         )

#                 except requests.exceptions.RequestException as e:
#                     st.error(f"API 调用失败：{e}")

# # -------------------------------------------------
# # Trigger Button
# # -------------------------------------------------
# st.divider()

# if st.button("📤 提交结果到服务器", type="primary"):
#     submit_dialog(df, option)
