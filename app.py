import streamlit as st
import pandas as pd
import json
import os
from PIL import Image
import tempfile
import subprocess
import unicodedata

st.set_page_config(page_title="Log Analiz Paneli", layout="wide")

st.title("Akıllı Log Analiz Paneli")

st.sidebar.header("Log Dosyası Yükle")
uploaded_file = st.sidebar.file_uploader("Bir log dosyası seç (.txt)", type=["txt"])

# --- Config Yükleme ---
st.sidebar.header("Config Dosyası Yükle (Opsiyonel)")
uploaded_config = st.sidebar.file_uploader("Bir config dosyası seç (config.json)", type=["json"])

if uploaded_config:
    config_content = uploaded_config.read().decode("utf-8")
    with open("config.json", "w") as f:
        f.write(config_content)
    st.sidebar.success("Config dosyası yüklendi ve kaydedildi!")

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

# --- Tema ve Stil ---
st.markdown(
    """
    <style>
    .main {background-color: #f5f7fa;}
    .stMetric {background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px #eee;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Ekstra Bilgi ---
st.sidebar.markdown("---")
st.sidebar.subheader("Hakkında")
st.sidebar.info("""
Akıllı Log Analiz Paneli

Bu uygulama, yüklediğiniz log dosyalarını analiz ederek özetler, grafikler ve anomali tespitleri sunar.
""")
st.sidebar.subheader("Yardım")
st.sidebar.info("""
- Log dosyanızı yükleyin.
- Anomali tespit ayarlarını yapın.
- Sonuçları ana panelde inceleyin.
- Sorun yaşarsanız sayfayı yenileyin.
""")

# --- Dosya Önizlemesi ---
if uploaded_file:
    st.sidebar.write("Dosya önizlemesi:")
    st.sidebar.code(content[:300])  # İlk 300 karakteri göster

# --- Genel Özet (Kartlar ve İkonlar) ---
st.header("Genel Özet")
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Log", report["total_logs"])
col2.metric("Kritik Log", report["critical_logs"])
col3.metric("Normal Log", report["non_critical_logs"])

# --- Analiz Raporunu İndir ---
st.download_button(
    label="Analiz Sonucunu İndir (JSON)",
    data=json.dumps(report, ensure_ascii=False, indent=2),
    file_name="analiz_raporu.json",
    mime="application/json"
)

# --- Olay Türleri ---
st.header("Olay Türleri")
event_df = pd.DataFrame({"#": range(1, len(report["events"])+1), "Olay Türü": report["events"]})
st.dataframe(event_df, use_container_width=True)

# --- Grafiksel Dağılım ---
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

def normalize_error_message(msg):
    # Büyük/küçük harf, baştaki/sondaki boşluk, Türkçe karakter normalize
    msg = msg.strip().lower()
    msg = unicodedata.normalize('NFKC', msg)
    return msg

# --- Hata Mesajları (Expander ile) ---
st.header("En Çok Görülen Hata Mesajları")
if "error_messages" in report and report["error_messages"]:
    from collections import Counter
    raw_msgs = report["error_messages"]
    norm_counter = Counter()
    norm_to_original = {}
    for msg, count in raw_msgs.items():
        norm = normalize_error_message(msg)
        norm_counter[norm] += count
        if norm not in norm_to_original or count > norm_counter[norm_to_original[norm]]:
            norm_to_original[norm] = msg
    error_df = pd.DataFrame({
        "Hata Mesajı": [norm_to_original[norm] for norm in norm_counter],
        "Adet": [norm_counter[norm] for norm in norm_counter]
    })
    with st.expander("Hata Mesajı Dağılımı Tablosu", expanded=True):
        st.dataframe(error_df)
    with st.expander("Hata Mesajı Bar Grafiği", expanded=False):
        st.bar_chart(error_df.set_index("Hata Mesajı"))
else:
    st.info("Hata mesajı dağılımı bulunamadı.")

# --- Zaman Serisi Grafiği ---
st.header("Zaman Serisi Grafiği")
img_path = "results/log_error_timeseries.png"
if os.path.exists(img_path):
    st.image(Image.open(img_path), caption="Zaman Serisi: Log ve Hata Sayısı")
else:
    st.info("Zaman serisi grafiği bulunamadı.")

# --- Anomali Algoritması Parametreleri ---
st.sidebar.header("Anomali Tespit Ayarları")
window_size = st.sidebar.number_input("Pencere Boyutu (dakika)", min_value=2, max_value=30, value=5, step=1)
threshold = st.sidebar.slider("Eşik (σ)", min_value=0.5, max_value=5.0, value=3.0, step=0.1)
with open("anomaly_config.json", "w") as f:
    json.dump({"window": window_size, "threshold": threshold}, f)

# --- Analizi Yeniden Başlat Butonu ---
if st.sidebar.button("Analizi Yeniden Başlat (Anomali Ayarları ile)"):
    with st.spinner("LLM ile analiz tekrar başlatılıyor..."):
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("main.py çalıştırılırken hata oluştu:")
            st.text(result.stderr)
            st.stop()
        else:
            st.success("Log analizi tekrarlandı! Sonuçlar güncellendi.")
    st.rerun()

# --- Seçili Anomali Parametreleri Kutusu ---
st.info(f"**Anomali Tespit Ayarları:**\n\n- Pencere Boyutu: {window_size} dakika\n- Eşik: {threshold}σ")

# --- Anomali Tespitleri (Expander ile) ---
st.header("Anomali Tespitleri")
if (
    ("anomalies" in report and report["anomalies"]) or
    ("error_message_anomalies" in report and report["error_message_anomalies"]) or
    ("duration_anomalies" in report and report["duration_anomalies"])
):
    if "anomalies" in report and report["anomalies"]:
        with st.expander("Zaman Serisi Anomalileri", expanded=True):
            for anomaly in report["anomalies"]:
                st.warning(f"Anomali: {anomaly}")
                try:
                    ts, rest = anomaly.split(": ", 1)
                    count = rest.split(" log")[0]
                    st.info(f"Bu dakikada {count} log kaydedildi.\n\nAnomali olarak işaretlenmesinin sebebi: Son {window_size} dakikadaki ortalama ve standart sapmaya göre bu değer, eşik olarak belirlediğiniz {threshold}σ'yı aşıyor.")
                except Exception:
                    pass
    else:
        st.info("Zaman serisi anomali tespit edilmedi.")
    if "error_message_anomalies" in report and report["error_message_anomalies"]:
        with st.expander("Hata Mesajı Anomalileri", expanded=False):
            for anomaly in report["error_message_anomalies"]:
                st.warning(f"Anomali: {anomaly}")
    else:
        st.info("Hata mesajı anomalisi tespit edilmedi.")
    if "duration_anomalies" in report and report["duration_anomalies"]:
        with st.expander("DURATION (İşlem Süresi) Anomalileri", expanded=False):
            for anomaly in report["duration_anomalies"]:
                st.warning(f"Anomali: {anomaly}")
    else:
        st.info("DURATION (işlem süresi) anomalisi tespit edilmedi.")
else:
    st.info("Anomali tespit edilmedi.")


# Analiz edilen log dosyasını göster
st.sidebar.markdown("---")
if uploaded_file:
    st.sidebar.success(f"Yüklenen dosya: {uploaded_file.name}")
    st.info(f"Analiz edilen dosya: logs/logs.txt (yüklenen dosyanın kopyası)")
else:
    st.info("Analiz edilen dosya: logs/server.txt")


