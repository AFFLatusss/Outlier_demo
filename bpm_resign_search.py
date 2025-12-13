# import pyodbc
# import xml.etree.ElementTree as ET
# import streamlit as st
# import io
# import csv


# def parse_tasks_from_memo(memo_xml: str, search_assignee: str):
#     """Parse BPMN XML memo and return tasks that match the assignee."""
#     tasks = []
#     if memo_xml is None:
#         return tasks
#     try:
#         root = ET.fromstring(memo_xml)
#     except Exception:
#         return tasks

#     ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
#     for task in root.findall(".//bpmn2:userTask[@assignee]", ns):
#         assignee = task.get("assignee")
#         if assignee == search_assignee:
#             tasks.append({
#                 "task_name": task.get("name"),
#                 "assignee": assignee,
#             })
#     return tasks


# def search_workflows(conn_str: str, search_assignee: str):
#     """Query database and return flattened results for display."""
#     try:
#         conn = pyodbc.connect(conn_str)
#     except Exception as e:
#         raise RuntimeError(f"Database connection failed: {e}")

#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             """
#             SELECT bpm_workflow_name, bpm_workflow_memo
#             FROM bpm_workflow_det
#             """
#         )
#     except Exception as e:
#         conn.close()
#         raise RuntimeError(f"Query failed: {e}")

#     results = []
#     for workflow_name, memo_xml in cursor.fetchall():
#         matched = parse_tasks_from_memo(memo_xml, search_assignee)
#         for t in matched:
#             results.append({
#                 "Workflow": workflow_name,
#                 "Task Name": t["task_name"],
#                 "Assignee": t["assignee"],
#             })

#     conn.close()
#     return results


# def make_conn_str(driver: str, server: str, database: str, uid: str, pwd: str) -> str:
#     return f"Driver={{{{ {driver} }}}};Server={server};Database={database};UID={uid};PWD={pwd};"


# st.set_page_config(page_title="BPM Assignee Search", layout="wide")
# st.title("BPM UserTask Assignee Search")
# st.write("Search BPMN user tasks by exact assignee from the Linecore BPM database.")

# with st.sidebar:
#     st.header("Database Settings")
#     driver = st.text_input("ODBC Driver", value="ODBC Driver 17 for SQL Server")
#     server = st.text_input("Server", value="10.168.1.94")
#     database = st.text_input("Database", value="LinecoreBPM")
#     uid = st.text_input("UID", value="baruser")
#     pwd = st.text_input("PWD", value="admin111.", type="password")

#     st.header("Search")
#     search_assignee = st.text_input("Assignee", value="L000102")
#     run_search = st.button("Search")

# if run_search:
#     conn_str = make_conn_str(driver.strip(), server.strip(), database.strip(), uid.strip(), pwd)
#     with st.spinner("Searching workflows..."):
#         try:
#             rows = search_workflows(conn_str, search_assignee.strip())
#         except Exception as e:
#             st.error(str(e))
#             rows = []

#     if rows:
#         st.success(f"Found {len(rows)} matching tasks for assignee '{search_assignee}'.")
#         st.dataframe(rows, use_container_width=True)

#         # Provide CSV download
#         output = io.StringIO()
#         writer = csv.DictWriter(output, fieldnames=["Workflow", "Task Name", "Assignee"])
#         writer.writeheader()
#         writer.writerows(rows)
#         csv_bytes = output.getvalue().encode("utf-8")
#         st.download_button(
#             label="Download CSV",
#             data=csv_bytes,
#             file_name=f"bpm_tasks_{search_assignee}.csv",
#             mime="text/csv",
#         )
#     else:
#         st.warning(f"No tasks found for assignee '{search_assignee}'.")
# else:
#     st.info("Enter connection details and an assignee, then click Search.")




# import streamlit as st
# import pymssql
# import xml.etree.ElementTree as ET

# st.title("BPM 指定账号查询")

# # Input field for the assignee
# search_assignee = st.text_input("输入指定账号(e.g., L000102):")

# if search_assignee:
#     # Connect to SQL Server using pymssql
#     conn = pymssql.connect(
#         server="10.168.1.94",
#         user="baruser",
#         password="admin111.",
#         database="LinecoreBPM",
#         port=1433  # default SQL Server port, change if needed
#     )
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT bpm_workflow_name, bpm_workflow_memo
#         FROM bpm_workflow_det
#     """)

#     final_result = []

#     for workflow_name, memo_xml in cursor.fetchall():
#         if memo_xml is None:
#             continue

#         try:
#             root = ET.fromstring(memo_xml)
#         except Exception:
#             continue

#         tasks = []
#         ns = {'bpmn2': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

#         # Find <userTask> nodes with assignee attribute
#         for task in root.findall(".//bpmn2:userTask[@assignee]", ns):
#             assignee = task.get("assignee")
#             if assignee == search_assignee:
#                 tasks.append({
#                     "name": task.get("name"),
#                     "assignee": assignee,
#                 })

#         if tasks:
#             final_result.append({
#                 "workflow_name": workflow_name,
#                 "tasks": tasks
#             })

#     # Display results
#     if final_result:
#         for wf in final_result:
#             st.subheader(f"流程: {wf['workflow_name']}")
#             for t in wf["tasks"]:
#                 st.write(f"- 节点: {t['name']}, 指定人: {t['assignee']}")
#     else:
#         st.info("No matching tasks found.")

import streamlit as st
import pymssql
import xml.etree.ElementTree as ET
import pandas as pd

# -------------------------
# Page setup
# -------------------------
st.set_page_config(
    page_title="BPM 指定账号查询",
    layout="wide"
)

st.title("🔍 BPM 流程指定人查询")
st.caption("按指定账号查询 BPM 流程中的 UserTask 节点")

# -------------------------
# Input
# -------------------------
search_assignee = st.text_input(
    "输入指定账号（例如：L000102）",
    placeholder="L000102"
)

# -------------------------
# Search
# -------------------------
if search_assignee:

    with st.spinner("正在查询数据库，请稍候..."):
        try:
            # ---- DB connection (pymssql) ----
            conn = pymssql.connect(
                server="10.168.1.94",
                user="baruser",
                password="admin111.",
                database="LinecoreBPM",
                port=1433
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT bpm_workflow_name, bpm_workflow_memo
                FROM bpm_workflow_det
            """)

            rows = cursor.fetchall()
            conn.close()

        except Exception as e:
            st.error(f"数据库连接失败: {e}")
            st.stop()

    results = []

    # BPMN namespace
    ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}

    for workflow_name, memo_xml in rows:
        if not memo_xml:
            continue

        try:
            root = ET.fromstring(memo_xml)
        except Exception:
            continue

        for task in root.findall(".//bpmn2:userTask[@assignee]", ns):
            assignee = task.get("assignee")
            if assignee == search_assignee:
                results.append({
                    "流程名称": workflow_name,
                    "节点名称": task.get("name"),
                    "指定人": assignee
                })

    # -------------------------
    # Display
    # -------------------------
    if results:
        df = pd.DataFrame(results)

        st.success(f"✅ 找到 {len(df)} 个匹配节点")

        st.divider()

        # ---- Grouped display (BIG CELL effect) ----
        for workflow, g in df.groupby("流程名称"):
            st.markdown(f"### 🧩 {workflow}")

            sub_df = g[["节点名称", "指定人"]].reset_index(drop=True)

            st.table(sub_df)

            st.divider()

        # ---- CSV Download ----
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "⬇️ 下载 CSV",
            data=csv,
            file_name=f"BPM_Assignee_{search_assignee}.csv",
            mime="text/csv"
        )

    else:
        st.info("未找到匹配的流程节点")

else:
    st.info("👆 请输入指定账号后开始查询")
