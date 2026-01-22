import io
import base64
import zipfile
from datetime import datetime
import time

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils import huafeng, liandong, spea
from utils.plot import plot_scatter


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def fig_to_png_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return buf


# =============================
# Page Config
# =============================
st.set_page_config(page_title="散点图分析工具")
st.title("📄 测试数据散点图分析")


# =============================
# Mode Selection
# =============================
outlier_mode = st.toggle("离散点模式")


# =============================
# Reader mapping
# =============================
CSV_READERS = {
    "FT-001": spea.read_csv,
    "FT-002": spea.read_csv,
    "FT-003": liandong.read_csv,
    "FT-006": huafeng.read_csv,
}


# =============================
# Data Loading
# =============================
if outlier_mode:
    equipment = st.selectbox(
        "选择测试设备",
        options=tuple(CSV_READERS.keys()),
        index=None,
        placeholder="请选择设备...",
    )

    if not equipment:
        st.error("请先选择测试设备", icon="🚨")
        st.stop()

    uploaded_file = st.file_uploader("📂 上传测试数据 (CSV 格式)", type="csv")
    if not uploaded_file:
        st.info("等待上传 CSV 测试数据。")
        st.stop()

    reader_func = CSV_READERS[equipment]

    with st.spinner("处理中，请稍候..."):
        try:
            details_df, units_df = reader_func(uploaded_file, type="graphs")
            df = pd.concat([units_df, details_df], ignore_index=True)
        except ValueError as e:
            st.error(str(e), icon="🚨")
            st.stop()

else:
    uploaded_file = st.file_uploader(
        "📂 上传测试数据 (xlsx 格式，请勿加密)",
        type="xlsx",
        help="仅支持单个未加密的 .xlsx 文件",
    )

    if not uploaded_file:
        st.info("👆 请上传一个 XLSX 文件以开始分析。")
        st.stop()

    @st.cache_data(show_spinner="正在读取 Excel 文件...")
    def load_excel(file):
        df = pd.read_excel(file)
        if df.empty:
            raise ValueError("上传的文件为空或无法读取。")
        return df

    try:
        df = load_excel(uploaded_file)
    except Exception as e:
        st.error(f"读取 Excel 文件失败: {e}")
        st.stop()

    if df.shape[1] < 7:
        st.error("数据列数不足（至少需要7列），请检查文件格式。")
        st.stop()


# =============================
# Parameter Selection
# =============================
parameter_columns = df.columns[6:].tolist()
if not parameter_columns:
    st.error("未检测到有效的参数列（从第7列开始）。")
    st.stop()

selected_columns = st.multiselect(
    "🔍 选择要分析的参数列（列名）：",
    options=parameter_columns,
    placeholder="选择要分析的参数列",
)

if not selected_columns:
    st.info("请至少选择一个参数列进行分析。")
    st.stop()


# =============================
# Validation Helper
# =============================
def validate_series(series: pd.Series):
    try:
        float(series.iloc[1])
        float(series.iloc[2])
        return True, ""
    except Exception:
        return False, "数据格式异常：前3行应为 单位 / 下限 / 上限"


# =============================
# Plot Options
# =============================
PLOT_STYLE_MAP = {"点": "scatter", "线": "line"}
plot_style = st.segmented_control(
    "制图样式",
    PLOT_STYLE_MAP.keys(),
    default="线",
)

PLOT_MODE_MAP = {"分别制图": "separate", "合并制图": "merge"}
plot_mode = None
if outlier_mode:
    plot_mode = st.segmented_control(
        "制图方式",
        PLOT_MODE_MAP.keys(),
        default="分别制图",
    )


# =============================
# Plotting
# =============================
if st.button("4) 生成", type="primary"):
    st.subheader("📊 散点图分析结果")

    progress_bar = st.progress(0.0)
    status_text = st.empty()

    html_sections = []
    png_files = {}

    total_tasks = 1 if (outlier_mode and plot_mode == "合并制图") else len(selected_columns)
    completed = 0

    # -------- Merged Plot --------
    if outlier_mode and plot_mode == "合并制图":
        upper_bounds = [df[col].iloc[1] for col in selected_columns]
        lower_bounds = [df[col].iloc[2] for col in selected_columns]

        if len(set(upper_bounds)) > 1 or len(set(lower_bounds)) > 1:
            st.warning("合并制图要求所有列属于相同的测试类型。")
            st.stop()

        try:
            status_text.text("正在生成合并散点图...")
            fig = plot_scatter(
                df[selected_columns],
                test_name=selected_columns,
                type=PLOT_STYLE_MAP[plot_style],
                outlier_mode=True,
                merge=True,
            )

            st.pyplot(fig)

            img64 = fig_to_base64(fig)
            html_sections.append(f"""
            <section class="plot">
              <h2>合并散点图</h2>
              <img src="data:image/png;base64,{img64}">
            </section>
            """)

            png_files["merged_plot.png"] = fig_to_png_bytes(fig)
            plt.close(fig)

            completed += 1
            progress_bar.progress(completed / total_tasks)
            status_text.text(f"正在生成图像 {completed} / {total_tasks}")

        except Exception as e:
            st.error(f"绘制失败: {e}")

    # -------- Separate Plots --------
    else:
        containers = (
            st.tabs(selected_columns)
            if len(selected_columns) > 1
            else [st.container()]
        )

        for container, col in zip(containers, selected_columns):
            with container:
                status_text.text(f"正在生成：{col}")
                series = df[col]
                valid, msg = validate_series(series)
                if not valid:
                    st.warning(f"列 '{col}' 数据格式异常: {msg}")
                    continue

                try:
                    fig = plot_scatter(
                        series,
                        test_name=col,
                        type=PLOT_STYLE_MAP[plot_style],
                        outlier_mode=outlier_mode,
                    )

                    st.pyplot(fig)

                    img64 = fig_to_base64(fig)
                    html_sections.append(f"""
                    <section class="plot">
                      <h2>{col}</h2>
                      <img src="data:image/png;base64,{img64}">
                    </section>
                    """)

                    safe_name = col.replace("/", "_").replace(" ", "_")
                    png_files[f"{safe_name}.png"] = fig_to_png_bytes(fig)
                    plt.close(fig)

                    completed += 1
                    progress_bar.progress(completed / total_tasks)
                    status_text.text(f"正在生成图像 {completed} / {total_tasks}")

                    time.sleep(0.001)

                except Exception as e:
                    st.error(f"绘制 '{col}' 失败: {e}")

    progress_bar.progress(1.0)
    status_text.success("✅ 图像生成完成")

    # -------- Export --------
    if html_sections:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh">
        <head>
          <meta charset="utf-8">
          <title>散点图分析报告</title>
          <style>
            body {{ font-family: Arial, sans-serif; padding: 24px; }}
            h1 {{ text-align: center; margin-bottom: 32px; }}
            .plot {{ margin-bottom: 32px; page-break-inside: avoid; }}
            img {{ width: 100%; max-width: 1000px; margin: 0 auto; display: block; }}
            @page {{ size: A4; margin: 15mm; }}
          </style>
        </head>
        <body>
          <h1>散点图分析报告</h1>
          <p style="text-align:center;">生成时间：{timestamp}</p>
          {''.join(html_sections)}
        </body>
        </html>
        """

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "🌐 下载 HTML 报告（浏览器转 PDF）",
                data=html_content,
                file_name="scatter_report.html",
                mime="text/html",
            )

        with col2:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, buf in png_files.items():
                    zf.writestr(name, buf.getvalue())

            zip_buffer.seek(0)

            st.download_button(
                "📦 下载所有图像 (ZIP)",
                data=zip_buffer,
                file_name="scatter_plots.zip",
                mime="application/zip",
            )
