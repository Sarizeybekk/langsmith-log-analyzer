
import streamlit as st
import pandas as pd
import json
import os
from PIL import Image
import tempfile
import subprocess

st.set_page_config(page_title="Log Analiz Paneli", layout="wide")

st.title("Akıllı Log Analiz Paneli")

st.sidebar.header("Log Dosyası Yükle")
uploaded_file = st.sidebar.file_uploader("Bir log dosyası seç (.txt)", type=["txt"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", dir="logs", mode="w") as tmp:
        content = uploaded_file.read().decode("utf-8")
        tmp.write(content)
        tmp_path = tmp.name


    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    saved_path = os.path.join(logs_dir, "logs.txt")
    with open(saved_path, "w") as f:
        f.write(content)

    with st.spinner("LLM ile analiz ediliyor..."):
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("main.py çalıştırılırken hata oluştu:")
            st.text(result.stderr)
            st.stop()
        else:
            st.success("Log analizi tamamlandı!")

report_path = "results/report.json"
if not os.path.exists(report_path):
    st.warning("Henüz bir analiz raporu bulunamadı. Lütfen log yükleyin.")
    st.stop()

with open(report_path, "r") as f:
    report = json.load(f)

st.header("Genel Özet")
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Log", report["total_logs"])
col2.metric("Kritik Log", report["critical_logs"])
col3.metric("Normal Log", report["non_critical_logs"])

st.header("Olay Türleri")
event_df = pd.DataFrame({"#": range(1, len(report["events"])+1), "Olay Türü": report["events"]})
st.dataframe(event_df, use_container_width=True)

st.header("Grafiksel Dağılım")
chart_dir = "results/charts"

col1, col2 = st.columns(2)

with col1:
    img_path = os.path.join(chart_dir, "event_type_distribution.png")
    if os.path.exists(img_path):
        st.image(Image.open(img_path), caption="Olay Türü Dağılımı")
    else:
        st.info("event_type_distribution.png bulunamadı")

with col2:
    img_path = os.path.join(chart_dir, "critical_vs_normal.png")
    if os.path.exists(img_path):
        st.image(Image.open(img_path), caption="Kritik vs Normal")
    else:
        st.info("critical_vs_normal.png bulunamadı")


