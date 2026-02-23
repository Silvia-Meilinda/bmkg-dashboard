"""
pages/1_📊_Dashboard_Utama.py
Halaman utama: KPI cards, charts utama, heatmap, insight & rekomendasi
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Utama – BMKG", page_icon="📊", layout="wide")

# CSS sama persis dgn app.py (harus diulang di setiap page)
from app import inject_css
inject_css()

from utils.data_loader import get_hourly_aggregation, get_daily_aggregation
from utils.charts import (make_temp_chart, make_rain_chart, make_wind_chart,
                           make_wind_rose, make_heatmap)
from utils.insights import generate_insights, generate_recommendations

# ── Ambil data dari session_state (sudah diload di app.py) ───────────────────
if "df" not in st.session_state:
    st.error("⚠️ Data belum dimuat. Kembali ke halaman utama dulu.")
    st.stop()

df     = st.session_state["df"]
df_h   = st.session_state["df_hourly"]
cfg    = st.session_state.get("config", {})
suhu_t = cfg.get("suhu_thr", 35.0)
hujan_t= cfg.get("hujan_thr", 20.0)
angin_t= cfg.get("angin_thr", 40.0)

# ── Header ────────────────────────────────────────────────────────────────────
from utils.helpers import now_wib
nwib = now_wib()

c1, c2 = st.columns([3,1])
with c1:
    st.markdown("""
    <h1 style='font-family:Syne,sans-serif;font-size:1.7rem;font-weight:800;margin:0;color:#e2edf8;'>
        Dashboard Analitik Cuaca — BMKG Juanda
    </h1>
    <p style='font-family:Space Mono,monospace;font-size:10px;color:#6b8aaa;margin:4px 0 0;
    text-transform:uppercase;letter-spacing:1px;'>
        Monitoring Internal · Agregasi Per Jam · Data Real Surabaya
    </p>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div style='text-align:right;padding-top:10px;'>
        <span style='background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.25);
        padding:4px 12px;border-radius:20px;font-family:Space Mono,monospace;font-size:11px;color:#00ffc8;'>
            ● LIVE
        </span><br>
        <span style='font-family:Space Mono,monospace;font-size:10px;color:#6b8aaa;'>
            {nwib.strftime('%d %b %Y %H:%M')} WIB
        </span>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Alerts ────────────────────────────────────────────────────────────────────
insights = generate_insights(df_h, df, suhu_t, hujan_t, angin_t)
for ins in [i for i in insights if i["level"] == "alert"][:2]:
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(255,184,0,0.08),rgba(255,107,53,0.06));
    border:1px solid rgba(255,184,0,0.3);border-left:4px solid #ffb800;border-radius:8px;
    padding:10px 16px;margin-bottom:10px;font-family:Space Mono,monospace;font-size:12px;color:#ffb800;'>
        ⚠️ <strong>PERINGATAN:</strong> {ins["text"]}
    </div>""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, icon, val, unit, delta_txt, color, val_class):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{icon} {label}</div>
        <div class='{val_class}'>{val}<span style='font-size:1rem;color:#6b8aaa;font-weight:400;'> {unit}</span></div>
        <div class='kpi-change' style='color:{color};margin-top:4px;font-family:Space Mono,monospace;font-size:11px;'>
            {delta_txt}
        </div>
    </div>""", unsafe_allow_html=True)

suhu_now  = df_h["suhu_avg"].mean()   if "suhu_avg"    in df_h.columns else 0
hujan_now = df_h["hujan_total"].sum() if "hujan_total" in df_h.columns else 0
angin_now = df_h["angin_avg"].mean()  if "angin_avg"   in df_h.columns else 0
lembap_now= df_h["lembap_avg"].mean() if "lembap_avg"  in df_h.columns else 0

# Tren: banding 12 jam pertama vs 12 jam terakhir
def delta_12h(col):
    if col not in df_h.columns or len(df_h) < 24: return 0
    h = len(df_h) // 2
    return df_h[col].tail(h).mean() - df_h[col].head(h).mean()

kpi(k1,"Suhu Rata-rata","🌡️",f"{suhu_now:.1f}","°C",
    f"{'↑' if delta_12h('suhu_avg')>0 else '↓'} {abs(delta_12h('suhu_avg')):.1f}°C",
    "#ff5555" if delta_12h('suhu_avg')>0 else "#00ffc8","kpi-value-temp")
kpi(k2,"Total Curah Hujan","🌧️",f"{hujan_now:.1f}","mm",
    f"{'↑' if delta_12h('hujan_total')>0 else '↓'} {abs(delta_12h('hujan_total')):.1f} mm",
    "#ff5555" if delta_12h('hujan_total')>0 else "#00ffc8","kpi-value-rain")
kpi(k3,"Kecepatan Angin","💨",f"{angin_now:.1f}","km/h",
    f"{'↑' if delta_12h('angin_avg')>0 else '↓'} {abs(delta_12h('angin_avg')):.1f} km/h",
    "#ff5555" if delta_12h('angin_avg')>0 else "#00ffc8","kpi-value-wind")
kpi(k4,"Kelembapan","💧",f"{lembap_now:.0f}","%",
    f"{'↑' if delta_12h('lembap_avg')>0 else '↓'} {abs(delta_12h('lembap_avg')):.1f}%",
    "#ff5555" if delta_12h('lembap_avg')>0 else "#00ffc8","kpi-value-humid")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Utama ──────────────────────────────────────────────────────────────
st.markdown("#### 📈 Tren Per Jam")
tab_s, tab_r, tab_w, tab_wr = st.tabs(["🌡️ Suhu","🌧️ Hujan","💨 Kecepatan Angin","🧭 Arah Angin"])
with tab_s:  st.plotly_chart(make_temp_chart(df_h, suhu_t), use_container_width=True)
with tab_r:  st.plotly_chart(make_rain_chart(df_h, hujan_t), use_container_width=True)
with tab_w:  st.plotly_chart(make_wind_chart(df_h, angin_t), use_container_width=True)
with tab_wr: st.plotly_chart(make_wind_rose(df), use_container_width=True)

# ── Heatmap + Insight ─────────────────────────────────────────────────────────
ch, ci = st.columns([1.6, 1])
with ch:
    st.markdown("#### 🔥 Heatmap Intensitas Cuaca")
    hm_param = st.selectbox("Parameter Heatmap",
        ["hujan_total","suhu_avg","angin_avg","lembap_avg"],
        format_func=lambda x: {"hujan_total":"Curah Hujan","suhu_avg":"Suhu",
                                "angin_avg":"Angin","lembap_avg":"Kelembapan"}[x],
        label_visibility="collapsed")
    st.plotly_chart(make_heatmap(df_h, hm_param), use_container_width=True)

with ci:
    st.markdown("#### 💡 Insight Otomatis")
    for ins in insights[:5]:
        cls = {"alert":"alert","warn":"warn","info":"info","good":"good"}.get(ins["level"],"info")
        st.markdown(f"""
        <div class='insight-card insight-{cls}'>
            <div class='insight-type insight-type-{cls}'>{ins["icon"]} {ins["label"]}</div>
            <div class='insight-text'>{ins["text"]}</div>
        </div>""", unsafe_allow_html=True)

# ── Rekomendasi ───────────────────────────────────────────────────────────────
st.markdown("#### 📋 Rekomendasi Operasional")
recs = generate_recommendations(df_h, suhu_t, hujan_t, angin_t)
rc1, rc2 = st.columns(2)
for i, r in enumerate(recs):
    (rc1 if i%2==0 else rc2).markdown(f"""
    <div class='rekom-card'>
        <div style='font-size:20px;'>{r["icon"]}</div>
        <div>
            <div style='font-weight:700;font-size:13px;color:#e2edf8;margin-bottom:3px;'>{r["title"]}</div>
            <div style='font-size:12px;color:#6b8aaa;line-height:1.5;'>{r["text"]}</div>
        </div>
    </div>""", unsafe_allow_html=True)

# SDG
st.markdown("---")
st.markdown("""
<div class='sdg-section'>
    <div style='font-size:38px;'>🌍</div>
    <div>
        <div style='font-family:Syne,sans-serif;font-size:14px;font-weight:700;color:#e2edf8;'>
            SDG 13 — Climate Action
        </div>
        <div style='font-size:12px;color:#6b8aaa;line-height:1.6;margin:4px 0 8px;'>
            Sistem ini mendukung penanganan perubahan iklim melalui penyajian informasi analitik
            meteorologi berbasis data real BMKG Juanda untuk pengambilan keputusan operasional.
        </div>
        <span style='background:rgba(104,189,69,0.1);color:#68bd45;border:1px solid #68bd45;
        padding:2px 8px;border-radius:4px;font-family:Space Mono,monospace;font-size:10px;margin-right:6px;'>
            SDG 13 Climate Action
        </span>
        <span style='background:rgba(0,180,255,0.08);color:#00b4ff;border:1px solid #00b4ff;
        padding:2px 8px;border-radius:4px;font-family:Space Mono,monospace;font-size:10px;margin-right:6px;'>
            SDG 11 Sustainable Cities
        </span>
        <span style='background:rgba(255,107,53,0.08);color:#ff6b35;border:1px solid #ff6b35;
        padding:2px 8px;border-radius:4px;font-family:Space Mono,monospace;font-size:10px;'>
            SDG 9 Innovation
        </span>
    </div>
</div>""", unsafe_allow_html=True)
