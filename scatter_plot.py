import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.plot import plot_scatter  # Assuming it returns a matplotlib Figure

# --- Page Config ---
st.set_page_config(page_title="散点图分析工具", layout="wide")
st.title("📄 测试数据散点图分析")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "📂 上传测试数据 (xlsx 格式，请勿加密)",
    type="xlsx",
    accept_multiple_files=False,
    help="仅支持单个未加密的 .xlsx 文件"
)

if not uploaded_file:
    st.info("👆 请上传一个 XLSX 文件以开始分析。")
    st.stop()

# --- Cache the DataFrame reading for performance ---
@st.cache_data(show_spinner="正在读取 Excel 文件...")
def load_data(file):
    try:
        # Default header=0 → 第一行作为列名 (column names like "DC_Kelvin_P2")
        df = pd.read_excel(file)
        if df.empty:
            raise ValueError("上传的文件为空或无法读取。")
        return df
    except Exception as e:
        st.error(f"读取 Excel 文件失败: {str(e)}")
        st.stop()

df = load_data(uploaded_file)

# --- Basic Validation ---
if df.shape[1] < 7:
    st.error("数据列数不足（至少需要7列），请检查文件格式。")
    st.stop()

# Extract parameter columns (from column index 6 onward → actual measurement params)
# These will be STRING column NAMES (e.g., "DC_Kelvin_P2", "Resistance_R1", etc.)
parameter_columns = df.columns[6:].tolist()

if not parameter_columns:
    st.error("未检测到有效的参数列（从第7列开始）。请检查文件结构。")
    st.stop()



# --- Column Selection (by NAME, not number) ---
selected_columns = st.multiselect(
    "🔍 选择要分析的参数列（列名）：",
    options=parameter_columns,
    # default=parameter_columns[:5] if len(parameter_columns) >= 5 else parameter_columns,  # Pre-select first few
    help="多选列名，将为每个选中的参数生成散点图"
)

if not selected_columns:
    st.info("请至少选择一个参数列进行分析。")
    st.stop()

# --- Additional Validation for Selected Columns ---
def validate_series(s):
    """Basic check: row 0 = unit (str), row 1/2 = numeric bounds, row 3+ = data"""
    try:
        unit = s.iloc[0]
        lower = float(s.iloc[1])
        upper = float(s.iloc[2])
        return True, ""
    except:
        return False, "数据格式异常：前3行应为 单位 / 下限 / 上限"

if st.button("🚀 生成", type="primary"):

    # --- Plotting Section ---
    st.subheader("📊 散点图分析结果")

    # Use tabs for cleaner layout when multiple columns selected
    if len(selected_columns) > 1:
        tabs = st.tabs(selected_columns)
        for tab, col_name in zip(tabs, selected_columns):
            with tab:
                s = df[col_name]
                valid, msg = validate_series(s)
                if not valid:
                    st.warning(f"列 '{col_name}' 数据格式异常: {msg}")
                    continue
                try:
                    fig = plot_scatter(s)
                    st.pyplot(fig)
                    plt.close(fig)
                except Exception as e:
                    st.error(f"绘制 '{col_name}' 失败: {str(e)}")
    else:
        # Single selection
        col_name = selected_columns[0]
        s = df[col_name]
        valid, msg = validate_series(s)
        if not valid:
            st.warning(f"列 '{col_name}' 数据格式异常: {msg}")
        else:
            try:
                fig = plot_scatter(s)
                st.pyplot(fig)
                plt.close(fig)
            except Exception as e:
                st.error(f"绘制失败: {str(e)}")

    # --- Footer ---
    # st.caption("💡 文件格式要求：第1行为参数列名 → 第2行为单位 → 第3行为下限 → 第4行为上限 → 第5行起为测量数据。前6列通常为测试信息，可忽略。")