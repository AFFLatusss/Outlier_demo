import streamlit as st

import subprocess
import platform

st.set_page_config(page_title="IP Ping Tool", layout="wide")
st.title("IP 地址 Ping 工具")


def ping(ip, count=4, timeout=1):
    system = platform.system().lower()

    if system == "windows":
        cmd = [
            "ping",
            "-n", str(count),
            "-w", str(timeout * 1000),  # ms
            ip
        ]
    else:
        cmd = [
            "ping",
            "-c", str(count),
            "-W", str(timeout),         # seconds
            ip
        ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output = []
    for line in process.stdout:
        output.append(line)

    process.wait()

    return process.returncode == 0, "".join(output)

def get_ip_list():
    """
    Returns a list of IP records:
    [
        {"id": 1, "name": "Google DNS", "ip": "8.8.8.8"},
        ...
    ]
    """
    return [
        {"id": 1, "name": "Google DNS", "ip": "8.8.8.8"},
        {"id": 2, "name": "Cloudflare DNS", "ip": "1.1.1.1"},
        {"id": 3, "name": "Local Device", "ip": "10.168.1.95"},
    ]





tab1, tab2 = st.tabs(["🔍 单个 IP Ping", "📋 IP 列表 Ping"])

with tab1:
    st.subheader("输入 IP 地址进行 Ping")

    ip = st.text_input("IP 地址", placeholder="例如：8.8.8.8")

    if st.button("Ping", key="ping_single"):
        if not ip:
            st.warning("请输入 IP 地址")
        else:
            with st.spinner("正在 Ping..."):
                ok, output = ping(ip)

            if ok:
                st.success("✅ 主机可达")
            else:
                st.error("❌ 主机不可达")

            st.code(output)

with tab2:
    st.subheader("IP 列表")

    ip_list = get_ip_list()

    for idx, row in enumerate(ip_list):
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                st.write(row["name"])

            with col2:
                st.write(row["ip"])

            with col3:
                ping_clicked = st.button("Ping", key=f"ping_{idx}")

            if ping_clicked:
                with st.spinner(f"Pinging {row['ip']}..."):
                    ok, output = ping(row["ip"])

                if ok:
                    st.success(f"{row['ip']} 可达")
                else:
                    st.error(f"{row['ip']} 不可达")

                st.code(output)

            st.divider()

