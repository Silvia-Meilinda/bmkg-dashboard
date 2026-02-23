"""
pages/3_📋_Laporan_Per_Jam.py
Tabel agregasi per jam lengkap + filter + export CSV
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Laporan Per Jam – BMKG", page_icon="📋", layout="wide")

from app import inject_css
inject_css()

from utils.data_loader import get_hourly_aggregation

if "df" not in st.session_state:
    st.error("⚠️ Data belum dimuat.")
    st.stop()

df   = st.session_state["df"]
df_h = st.session_state["df_hourly"]

st.markdown("""
<h1 style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;color:#e2edf8;margin:0;'>
    📋 Laporan Agregasi Per Jam
</h1>
<p style='font-family:Space Mono,monospace;font-size:10px;color:#6b8aaa;margin:4px 0 16px;
text-transform:uppercase;letter-spacing:1px;'>
    Data menit → agregasi per jam · 5 file BMKG Juanda
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Filter tanggal ────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 1, 2])
all_dates = sorted(df_h["tanggal"].dt.date.unique()) if "tanggal" in df_h.columns else []

with c1:
    sel_date = st.selectbox("Pilih Tanggal", all_dates,
                             index=len(all_dates)-1 if all_dates else 0)
with c2:
    sel_param_sort = st.selectbox("Urutkan Berdasarkan",
        ["jam","suhu_avg","hujan_total","angin_max","lembap_avg"],
        format_func=lambda x: {"jam":"Jam","suhu_avg":"Suhu","hujan_total":"Hujan",
                                "angin_max":"Angin Max","lembap_avg":"Kelembapan"}[x])
with c3:
    sel_status = st.multiselect("Filter Status",
        ["Normal","Hujan","Kabut","Ekstrim"], default=["Normal","Hujan","Kabut","Ekstrim"])

# Filter data
df_hari = df_h[df_h["tanggal"].dt.date == sel_date].copy() if "tanggal" in df_h.columns else df_h.copy()
if sel_status and "status" in df_hari.columns:
    df_hari = df_hari[df_hari["status"].isin(sel_status)]
if sel_param_sort in df_hari.columns:
    df_hari = df_hari.sort_values(sel_param_sort)

# ── Ringkasan hari ─────────────────────────────────────────────────────────────
if not df_hari.empty:
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Suhu Max",  f"{df_hari['suhu_max'].max():.1f}°C"  if 'suhu_max'  in df_hari.columns else "-")
    m2.metric("Hujan Total",f"{df_hari['hujan_total'].sum():.1f}mm" if 'hujan_total' in df_hari.columns else "-")
    m3.metric("Angin Max", f"{df_hari['angin_max'].max():.1f}km/h" if 'angin_max'  in df_hari.columns else "-")
    m4.metric("Lembap Avg",f"{df_hari['lembap_avg'].mean():.0f}%" if 'lembap_avg' in df_hari.columns else "-")

st.markdown("#### 📊 Tabel Data")

# ── Siapkan tabel tampilan ────────────────────────────────────────────────────
display_map = {
    "jam_label":   "Jam",
    "suhu_avg":    "Suhu Avg (°C)",
    "suhu_min":    "Suhu Min (°C)",
    "suhu_max":    "Suhu Max (°C)",
    "lembap_avg":  "Kelembapan (%)",
    "dew_point_avg":"Dew Point (°C)",
    "hujan_total": "Hujan (mm)",
    "angin_avg":   "Angin Avg (km/h)",
    "angin_max":   "Angin Max (km/h)",
    "arah_angin":  "Arah Angin",
    "tekanan_avg": "Tekanan (mb)",
    "radiasi_avg": "Radiasi (W/m²)",
    "status":      "Status",
    "n_data":      "N Data",
}
show_cols = [k for k in display_map if k in df_hari.columns]
df_show = df_hari[show_cols].rename(columns=display_map).copy()

# Format kolom numerik
fmt = {v: "{:.1f}" for k,v in display_map.items()
       if k in ["suhu_avg","suhu_min","suhu_max","dew_point_avg",
                 "hujan_total","angin_avg","angin_max","tekanan_avg","radiasi_avg"]}
fmt["Kelembapan (%)"] = "{:.0f}"

# Style
def color_status(val):
    m = {"Ekstrim":"background:rgba(255,85,85,0.12);color:#ff5555;",
         "Hujan":  "background:rgba(74,158,255,0.1);color:#4a9eff;",
         "Kabut":  "background:rgba(255,184,0,0.1);color:#ffb800;",
         "Normal": "background:rgba(0,255,200,0.08);color:#00ffc8;"}
    return m.get(val,"")

def color_suhu(val):
    try:
        v=float(val)
        if v>=35:  return "color:#ff5555;"
        if v>=33:  return "color:#ff6b35;"
        if v>=30:  return "color:#ffb800;"
        return "color:#00ffc8;"
    except: return ""

s = df_show.style.format(fmt, na_rep="-")
if "Status" in df_show.columns:
    s = s.applymap(color_status, subset=["Status"])
if "Suhu Avg (°C)" in df_show.columns:
    s = s.applymap(color_suhu, subset=["Suhu Avg (°C)"])

st.dataframe(s, use_container_width=True, height=550)

# ── Export ────────────────────────────────────────────────────────────────────
st.markdown("---")
dl1, dl2 = st.columns(2)

with dl1:
    csv = df_hari.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("⬇️ Download Tabel Ini (CSV)",
        data=csv, file_name=f"laporan_bmkg_juanda_{sel_date}.csv", mime="text/csv")

with dl2:
    # Download semua data agregasi
    csv_all = df_h.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("⬇️ Download Semua Agregasi (CSV)",
        data=csv_all, file_name="laporan_bmkg_juanda_semua.csv", mime="text/csv")

# ── Catatan format ────────────────────────────────────────────────────────────
with st.expander("📝 Keterangan Kolom"):
    st.markdown("""
    | Kolom | Sumber | Keterangan |
    |-------|--------|-----------|
    | Suhu Avg (°C) | Temperature Average 1 min | Rata-rata suhu per jam |
    | Suhu Min/Max | Temperature Min/Max 10 min | Ekstrem suhu dalam jam |
    | Kelembapan (%) | Humidity Average 1 min | Kelembapan relatif rata-rata |
    | Dew Point (°C) | Dew Point Average 1 min | Titik embun rata-rata |
    | Hujan (mm) | Accumulated Precipitation 1 hour | Kumulatif hujan per jam |
    | Angin Avg (km/h) | Wind Speed Average 1 min (m/s × 3.6) | Rata-rata kecepatan angin |
    | Angin Max (km/h) | Wind Speed Maximum 1 min (m/s × 3.6) | Kecepatan angin tertinggi |
    | Arah Angin | Wind Direction Prevailing 1 min | Arah dominan dalam jam |
    | Tekanan (mb) | Pressure Average 1 min | Tekanan atmosfer rata-rata |
    | Radiasi (W/m²) | Solar Radiation Average 1 min | Radiasi surya rata-rata |
    | Status | Derived | Normal / Hujan / Kabut / Ekstrim |
    | N Data | Count | Jumlah data menit dalam jam tersebut |
    """)
