
import streamlit as st
import pymssql
import xml.etree.ElementTree as ET

st.title("BPM 指定账号查询")

# Input field for the assignee
search_assignee = st.text_input("输入指定账号(e.g., L000102):")

if search_assignee:
    # Connect to SQL Server using pymssql
    conn = pymssql.connect(
        server="10.168.1.94",
        user="baruser",
        password="admin111.",
        database="LinecoreBPM",
        port=1433  # default SQL Server port, change if needed
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bpm_workflow_name, bpm_workflow_memo
        FROM bpm_workflow_det
    """)

    final_result = []

    for workflow_name, memo_xml in cursor.fetchall():
        if memo_xml is None:
            continue

        try:
            root = ET.fromstring(memo_xml)
        except Exception:
            continue

        tasks = []
        ns = {'bpmn2': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

        # Find <userTask> nodes with assignee attribute
        for task in root.findall(".//bpmn2:userTask[@assignee]", ns):
            assignee = task.get("assignee")
            if assignee == search_assignee:
                tasks.append({
                    "name": task.get("name"),
                    "assignee": assignee,
                })

        if tasks:
            final_result.append({
                "workflow_name": workflow_name,
                "tasks": tasks
            })

    # Display results
    if final_result:
        for wf in final_result:
            st.subheader(f"流程: {wf['workflow_name']}")
            for t in wf["tasks"]:
                st.write(f"- 节点: {t['name']}, 指定人: {t['assignee']}")
    else:
        st.info("No matching tasks found.")
