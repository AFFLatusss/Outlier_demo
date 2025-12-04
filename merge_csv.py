import streamlit as st
import pandas as pd
import chardet
from io import StringIO, BytesIO

# --- Configuration and Title ---
# st.set_page_config(layout="wide")
st.title("📄 CSV 文件合并")

# Define the maximum number of bytes to read for encoding detection
CHUNK_SIZE_FOR_DETECTION = 100000 
COMMON_CHINESE_ENCODING = 'gb18030' 

# --- File Uploader ---
uploaded_files = st.file_uploader(
    "📂 上传数据 (CSV 格式)", 
    type="csv", 
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("⬆️ 请上传 CSV 文件以开始合并。")
    st.stop()

# --- Core Logic Functions ---

@st.cache_data(show_spinner=False)
def process_and_merge_files(uploaded_files):
    """
    Detects encoding for each file, reads it into a DataFrame using fallbacks,
    and then concatenates all successfully read DataFrames.
    """
    all_dfs = []
    log_messages = []
    
    # 1. Iteration and Processing
    for file in uploaded_files:
        file_name = file.name
        log_messages.append(f"--- 正在处理文件: {file_name} ---")
        
        # Read the file content as bytes for chardet
        bytes_data = file.read() 
        
        # 1.1 Detect Encoding using chardet
        detected_encoding = 'utf-8' # Default fallback
        
        try:
            # Analyze the raw bytes
            result = chardet.detect(bytes_data[:CHUNK_SIZE_FOR_DETECTION]) # Detect on a sample chunk
            
            if result['confidence'] > 0.7:
                detected_encoding = result['encoding'].lower()
        
        except Exception as e:
            log_messages.append(f"    - ⚠️ 警告: 未知编码，使用默认 UTF-8。错误: {e}")
            detected_encoding = 'utf-8'

        
        # 1.2 Read the CSV using the detected/fallback encoding
        df = None
        
        # Attempt 1: Detected/Default encoding
        try:
            # We use StringIO to wrap the decoded bytes data for pandas
            df = pd.read_csv(BytesIO(bytes_data), encoding=detected_encoding)
            # log_messages.append(f"    - ✅ 成功读取 (使用: {detected_encoding})")

        except UnicodeDecodeError:
            # Attempt 2: Try the robust Chinese encoding 'gb18030'
            try:
                df = pd.read_csv(BytesIO(bytes_data), encoding=COMMON_CHINESE_ENCODING)
                # log_messages.append(f"    - ✅ 成功读取 (使用 GB18030 后备方案)")

            except UnicodeDecodeError:
                # Attempt 3: Try 'latin1' for non-Unicode/European files
                try:
                    df = pd.read_csv(BytesIO(bytes_data), encoding='latin1')
                    # log_messages.append(f"    - ✅ 成功读取 (使用 Latin1 后备方案)")
                
                except Exception as e:
                    # Final failure handling
                    log_messages.append(f"    - ❌ 读取失败:文件已跳过。错误: {e}")
                    continue # Skip to the next file
        
        except Exception as e:
            # Handle other pd.read_csv errors (e.g., incorrect separator, empty file)
            log_messages.append(f"    - ❌ 结构错误: 文件读取失败。文件已跳过。错误: {e}")
            continue

        # Append the successfully read DataFrame
        if df is not None:
            all_dfs.append(df)
            
    
    # 2. Concatenation
    if not all_dfs:
        return None, log_messages

    try:
        big_df = pd.concat(all_dfs, ignore_index=True)
        log_messages.append("\n--- 合并结果 ---")
        log_messages.append(f"🎉 成功合并 {len(all_dfs)} 个文件。")
        log_messages.append(f"总行数: {len(big_df)} | 总列数: {len(big_df.columns)}")
        return big_df, log_messages
        
    except Exception as e:
        log_messages.append(f"\n❌ 合并失败。请检查文件列名是否完全一致。错误: {e}")
        return None, log_messages


# --- Streamlit UI Rendering ---

# The processing function runs when the button is clicked
if st.button("🚀 合并", type="primary"):
    with st.spinner("正在合并和处理文件..."):
        # The function handles all reading, encoding, and merging
        final_df, logs = process_and_merge_files(uploaded_files)
    
    st.subheader("🛠️ 处理日志")
    st.code("\n".join(logs), language="text")

    if final_df is not None:
        st.success("✅ 文件合并成功！")

        # Display Summary
        c1, c2 = st.columns(2)
        c1.metric("合并后的总行数 (Total Rows)", f"{len(final_df):,}")
        c2.metric("合并后的总列数 (Total Columns)", f"{len(final_df.columns)}")

        st.subheader("📊 合并结果预览 (前 5 行)")
        st.dataframe(final_df.head(), use_container_width=True)

        # Download Button
        # Create a buffer for the combined CSV file
        csv_buffer = BytesIO()
        # Save to buffer using UTF-8 for universal compatibility
        final_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)

        st.download_button(
            label="⬇️ 下载合并后的 CSV 文件 (UTF-8)",
            data=csv_buffer,
            file_name="combined_data.csv",
            mime="text/csv"
        )
    else:
        st.error("❌ 合并失败。请检查日志以获取详细信息。")