"""
BMKG Juanda - Dashboard Analitik Data Cuaca
Sistem Monitoring Internal - Agregasi Per Jam
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BMKG Juanda — Dashboard Analitik",
    page_icon="🌤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* Root Variables */
:root {
    --bg: #04080f;
    --surface: #0b1420;
    --accent: #00b4ff;
    --accent2: #00ffc8;
    --accent3: #ff6b35;
    --warn: #ffb800;
    --text: #e2edf8;
    --muted: #6b8aaa;
}

/* Global */
html, body, .stApp {
    background-color: #04080f !important;
    color: #e2edf8 !important;
    font-family: 'Syne', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0b1420 !important;
    border-right: 1px solid rgba(0,180,255,0.12) !important;
}

[data-testid="stSidebar"] * {
    color: #e2edf8 !important;
}

/* Main container */
.block-container {
    padding: 1.5rem 2rem !important;
    max-width: 100% !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #0b1420 !important;
    border: 1px solid rgba(0,180,255,0.12) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

[data-testid="stMetricValue"] {
    color: #00b4ff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
}

[data-testid="stMetricLabel"] {
    color: #6b8aaa !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

[data-testid="stMetricDelta"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #e2edf8 !important;
}

/* Selectbox, multiselect */
.stSelectbox > div, .stMultiSelect > div {
    background-color: #0b1420 !important;
    border-color: rgba(0,180,255,0.2) !important;
    color: #e2edf8 !important;
}

/* Dataframe */
.stDataFrame {
    background-color: #0b1420 !important;
}

/* Divider */
hr {
    border-color: rgba(0,180,255,0.12) !important;
}

/* Alert/info box */
.alert-box {
    background: linear-gradient(135deg, rgba(255,184,0,0.08), rgba(255,107,53,0.06));
    border: 1px solid rgba(255,184,0,0.3);
    border-left: 4px solid #ffb800;
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 16px;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: #ffb800;
}

/* KPI card custom */
.kpi-card {
    background: #0b1420;
    border: 1px solid rgba(0,180,255,0.12);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    transition: border-color 0.2s;
}

.kpi-card:hover {
    border-color: rgba(0,180,255,0.35);
}

.kpi-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #6b8aaa;
    margin-bottom: 8px;
}

.kpi-value-temp  { color: #ff6b35; font-size: 2.2rem; font-weight: 800; }
.kpi-value-rain  { color: #4a9eff; font-size: 2.2rem; font-weight: 800; }
.kpi-value-wind  { color: #00ffc8; font-size: 2.2rem; font-weight: 800; }
.kpi-value-humid { color: #00b4ff; font-size: 2.2rem; font-weight: 800; }

.kpi-change { font-family: 'Space Mono', monospace; font-size: 11px; margin-top: 4px; }
.kpi-change-up   { color: #ff5555; }
.kpi-change-down { color: #00ffc8; }

/* Insight card */
.insight-card {
    background: #111d2e;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-left: 3px solid transparent;
}
.insight-warn  { border-left-color: #ffb800; }
.insight-info  { border-left-color: #00b4ff; }
.insight-alert { border-left-color: #ff5555; }
.insight-good  { border-left-color: #00ffc8; }

.insight-type {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.insight-type-warn  { color: #ffb800; }
.insight-type-info  { color: #00b4ff; }
.insight-type-alert { color: #ff5555; }
.insight-type-good  { color: #00ffc8; }

.insight-text { font-size: 12px; color: #e2edf8; line-height: 1.5; }

/* Rekom card */
.rekom-card {
    background: #111d2e;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    gap: 10px;
    align-items: flex-start;
}

/* SDG section */
.sdg-section {
    background: #0b1420;
    border: 1px solid rgba(0,180,255,0.12);
    border-radius: 12px;
    padding: 18px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-top: 8px;
}

/* Status badge */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
}
.badge-normal  { background: rgba(0,255,200,0.1); color: #00ffc8; }
.badge-hujan   { background: rgba(74,158,255,0.12); color: #4a9eff; }
.badge-ekstrim { background: rgba(255,85,85,0.1); color: #ff5555; }
.badge-kabut   { background: rgba(255,184,0,0.1); color: #ffb800; }

/* Live badge */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,255,200,0.08);
    border: 1px solid rgba(0,255,200,0.25);
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #00ffc8;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0b1420; }
::-webkit-scrollbar-thumb { background: rgba(0,180,255,0.2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Import modules ────────────────────────────────────────────────────────────
from utils.data_loader import load_all_data, get_hourly_aggregation
from utils.charts import (
    make_temp_chart, make_rain_chart, make_wind_rose,
    make_heatmap, make_humidity_chart, make_multi_param_chart
)
from utils.insights import generate_insights, generate_recommendations
from utils.helpers import format_datetime_wib, get_status_badge

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    return load_all_data("data/")

df_raw = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
        <div style='font-size:36px;'>🌤</div>
        <div style='font-family:Syne,sans-serif; font-size:15px; font-weight:800; color:#e2edf8;'>
            BMKG Juanda
        </div>
        <div style='font-family:Space Mono,monospace; font-size:9px; color:#6b8aaa; letter-spacing:1px; text-transform:uppercase;'>
            Dashboard Analitik Internal
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigasi halaman
    st.markdown("**📍 Navigasi**")
    page = st.radio(
        "",
        ["🏠 Dashboard Utama", "📊 Analisis Tren", "📋 Laporan Per Jam", "⚙️ Pengaturan Data"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Filter Periode
    st.markdown("**🗓 Filter Periode**")
    periode = st.selectbox("Rentang Waktu", ["7 Hari Terakhir", "30 Hari Terakhir", "3 Bulan Terakhir", "Custom"])

    if periode == "Custom":
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Mulai", datetime.now() - timedelta(days=7))
        end_date = col2.date_input("Selesai", datetime.now())
    else:
        days_map = {"7 Hari Terakhir": 7, "30 Hari Terakhir": 30, "3 Bulan Terakhir": 90}
        n_days = days_map.get(periode, 7)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=n_days)

    # Filter Jam
    st.markdown("**🕐 Filter Jam**")
    jam_range = st.slider("Rentang Jam", 0, 23, (0, 23), format="%d:00")

    st.markdown("---")

    # File Sumber
    st.markdown("**📁 File Sumber Data**")
    available_files = df_raw["file_sumber"].unique().tolist() if "file_sumber" in df_raw.columns else ["Semua File"]
    selected_files = st.multiselect("Pilih File", available_files, default=available_files)

    st.markdown("---")

    # Thresholds
    st.markdown("**⚠️ Batas Peringatan**")
    suhu_threshold = st.number_input("Suhu Ekstrim (°C)", value=35.0, step=0.5)
    hujan_threshold = st.number_input("Hujan Lebat (mm/jam)", value=20.0, step=1.0)
    angin_threshold = st.number_input("Angin Kencang (km/h)", value=40.0, step=1.0)

    st.markdown("---")

    # Waktu WIB
    wib = pytz.timezone("Asia/Jakarta")
    now_wib = datetime.now(wib)
    st.markdown(f"""
    <div style='text-align:center;'>
        <div class='live-badge'>
            <span style='color:#ff4444;font-size:8px;'>●</span> LIVE
        </div>
        <div style='font-family:Space Mono,monospace; font-size:11px; color:#6b8aaa; margin-top:8px;'>
            {now_wib.strftime('%A, %d %B %Y')}<br>
            <strong style='color:#e2edf8;'>{now_wib.strftime('%H:%M:%S')} WIB</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Filter Data ───────────────────────────────────────────────────────────────
df = df_raw.copy()
if "tanggal" in df.columns:
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df = df[
        (df["tanggal"].dt.date >= start_date) &
        (df["tanggal"].dt.date <= end_date)
    ]
if "jam" in df.columns:
    df = df[(df["jam"] >= jam_range[0]) & (df["jam"] <= jam_range[1])]
if "file_sumber" in df.columns and selected_files:
    df = df[df["file_sumber"].isin(selected_files)]

df_hourly = get_hourly_aggregation(df)

# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN: DASHBOARD UTAMA
# ═══════════════════════════════════════════════════════════════════════════════
if "Dashboard Utama" in page:

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("""
        <div>
            <h1 style='font-family:Syne,sans-serif; font-size:1.8rem; font-weight:800; margin:0; color:#e2edf8;'>
                Dashboard Analitik Data Cuaca
            </h1>
            <p style='font-family:Space Mono,monospace; font-size:11px; color:#6b8aaa; margin:4px 0 0; text-transform:uppercase; letter-spacing:1px;'>
                BMKG Juanda — Surabaya · Sistem Monitoring Internal
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        st.markdown(f"""
        <div style='text-align:right; padding-top:10px;'>
            <span class='live-badge'>● LIVE DATA</span><br>
            <span style='font-family:Space Mono,monospace; font-size:10px; color:#6b8aaa;'>
                {now_wib.strftime('%d %b %Y %H:%M')} WIB
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Alert Banner
    alerts = generate_insights(df_hourly, suhu_threshold, hujan_threshold, angin_threshold)
    critical_alerts = [a for a in alerts if a["level"] == "alert"]
    if critical_alerts:
        for alert in critical_alerts[:2]:
            st.markdown(f"""
            <div class='alert-box'>
                ⚠️ <strong>PERINGATAN CUACA:</strong> {alert['text']}
            </div>
            """, unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    suhu_avg   = df["suhu"].mean()    if "suhu"   in df.columns else 31.4
    hujan_sum  = df["hujan"].sum()    if "hujan"  in df.columns else 18.7
    angin_avg  = df["angin"].mean()   if "angin"  in df.columns else 28.3
    lembap_avg = df["lembap"].mean()  if "lembap" in df.columns else 82.0

    suhu_delta  = df["suhu"].tail(24).mean()  - df["suhu"].head(24).mean()  if len(df) > 48 else 1.2
    hujan_delta = df["hujan"].tail(24).sum()  - df["hujan"].head(24).sum()  if len(df) > 48 else 3.5
    angin_delta = df["angin"].tail(24).mean() - df["angin"].head(24).mean() if len(df) > 48 else -5.1
    lembap_delta= df["lembap"].tail(24).mean()- df["lembap"].head(24).mean()if len(df) > 48 else 4.0

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>🌡️ Suhu Rata-rata</div>
            <div class='kpi-value-temp'>{suhu_avg:.1f}°C</div>
            <div class='kpi-change {"kpi-change-up" if suhu_delta > 0 else "kpi-change-down"}'>
                {"↑" if suhu_delta > 0 else "↓"} {abs(suhu_delta):.1f}°C dari sebelumnya
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>🌧️ Total Curah Hujan</div>
            <div class='kpi-value-rain'>{hujan_sum:.1f} mm</div>
            <div class='kpi-change {"kpi-change-up" if hujan_delta > 0 else "kpi-change-down"}'>
                {"↑" if hujan_delta > 0 else "↓"} {abs(hujan_delta):.1f} mm vs periode lalu
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>💨 Kecepatan Angin</div>
            <div class='kpi-value-wind'>{angin_avg:.1f} km/h</div>
            <div class='kpi-change {"kpi-change-up" if angin_delta > 0 else "kpi-change-down"}'>
                {"↑" if angin_delta > 0 else "↓"} {abs(angin_delta):.1f} km/h dari rata-rata
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>💧 Kelembapan</div>
            <div class='kpi-value-humid'>{lembap_avg:.0f}%</div>
            <div class='kpi-change {"kpi-change-up" if lembap_delta > 0 else "kpi-change-down"}'>
                {"↑" if lembap_delta > 0 else "↓"} {abs(lembap_delta):.1f}% dari rata-rata
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row 1 ──────────────────────────────────────────────────────────
    st.markdown("#### 📈 Tren Cuaca Per Jam")
    tab1, tab2, tab3 = st.tabs(["🌡️ Suhu", "🌧️ Curah Hujan", "💨 Angin"])

    with tab1:
        fig_temp = make_temp_chart(df_hourly)
        st.plotly_chart(fig_temp, use_container_width=True)

    with tab2:
        fig_rain = make_rain_chart(df_hourly)
        st.plotly_chart(fig_rain, use_container_width=True)

    with tab3:
        fig_wind = make_wind_rose(df_hourly)
        st.plotly_chart(fig_wind, use_container_width=True)

    # ── Charts Row 2 ──────────────────────────────────────────────────────────
    col_hm, col_rhs = st.columns([1.6, 1])

    with col_hm:
        st.markdown("#### 🔥 Heatmap Intensitas Cuaca")
        fig_hm = make_heatmap(df_hourly)
        st.plotly_chart(fig_hm, use_container_width=True)

    with col_rhs:
        st.markdown("#### 💡 Insight Otomatis")
        insights = generate_insights(df_hourly, suhu_threshold, hujan_threshold, angin_threshold)
        for ins in insights[:5]:
            cls_map = {"warn": "warn", "info": "info", "alert": "alert", "good": "good"}
            cls = cls_map.get(ins["level"], "info")
            st.markdown(f"""
            <div class='insight-card insight-{cls}'>
                <div class='insight-type insight-type-{cls}'>{ins["icon"]} {ins["label"]}</div>
                <div class='insight-text'>{ins["text"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Rekomendasi ───────────────────────────────────────────────────────────
    st.markdown("#### 📋 Rekomendasi Operasional")
    recoms = generate_recommendations(df_hourly, suhu_threshold, hujan_threshold, angin_threshold)
    rc1, rc2 = st.columns(2)
    for i, rec in enumerate(recoms):
        col = rc1 if i % 2 == 0 else rc2
        with col:
            st.markdown(f"""
            <div class='rekom-card'>
                <div style='font-size:20px;'>{rec["icon"]}</div>
                <div>
                    <div style='font-weight:700; font-size:13px; color:#e2edf8; margin-bottom:3px;'>{rec["title"]}</div>
                    <div style='font-size:12px; color:#6b8aaa; line-height:1.5;'>{rec["text"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── SDG Section ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"""
    <div class='sdg-section'>
        <div style='font-size:40px;'>🌍</div>
        <div>
            <div style='font-family:Syne,sans-serif; font-size:15px; font-weight:700; color:#e2edf8;'>
                SDG 13 — Climate Action
            </div>
            <div style='font-size:12px; color:#6b8aaa; line-height:1.6; margin: 4px 0 8px;'>
                Sistem ini mendukung <em>penanganan perubahan iklim</em> melalui penyajian informasi analitik
                meteorologi untuk pengambilan keputusan operasional di BMKG Juanda.
            </div>
            <span style='background:rgba(104,189,69,0.1); color:#68bd45; border:1px solid #68bd45;
                padding:2px 8px; border-radius:4px; font-family:Space Mono,monospace; font-size:10px; margin-right:6px;'>
                SDG 13 Climate Action
            </span>
            <span style='background:rgba(0,180,255,0.08); color:#00b4ff; border:1px solid #00b4ff;
                padding:2px 8px; border-radius:4px; font-family:Space Mono,monospace; font-size:10px; margin-right:6px;'>
                SDG 11 Sustainable Cities
            </span>
            <span style='background:rgba(255,107,53,0.08); color:#ff6b35; border:1px solid #ff6b35;
                padding:2px 8px; border-radius:4px; font-family:Space Mono,monospace; font-size:10px;'>
                SDG 9 Innovation
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN: ANALISIS TREN
# ═══════════════════════════════════════════════════════════════════════════════
elif "Analisis Tren" in page:
    st.markdown("## 📊 Analisis Tren Cuaca")
    st.markdown("Visualisasi mendalam pola cuaca historis per jam dari 6 file data meteorologi.")
    st.markdown("---")

    # Multi-parameter chart
    st.markdown("#### Parameter Gabungan")
    params = st.multiselect(
        "Pilih Parameter",
        ["Suhu (°C)", "Curah Hujan (mm)", "Angin (km/h)", "Kelembapan (%)"],
        default=["Suhu (°C)", "Curah Hujan (mm)"]
    )
    fig_multi = make_multi_param_chart(df_hourly, params)
    st.plotly_chart(fig_multi, use_container_width=True)

    # Statistik deskriptif
    st.markdown("#### 📐 Statistik Deskriptif")
    col_s = {"suhu": "Suhu (°C)", "hujan": "Hujan (mm)", "angin": "Angin (km/h)", "lembap": "Kelembapan (%)"}
    stat_df = df[[k for k in col_s.keys() if k in df.columns]].rename(columns=col_s)
    st.dataframe(
        stat_df.describe().round(2).style
            .background_gradient(cmap="Blues", axis=None)
            .format("{:.2f}"),
        use_container_width=True
    )

    # Distribusi per jam
    st.markdown("#### 🕐 Pola Rata-rata Per Jam dalam Sehari")
    if "jam" in df.columns and "suhu" in df.columns:
        hourly_mean = df.groupby("jam")[["suhu", "hujan", "angin", "lembap"]].mean().reset_index()
        fig_hr = go.Figure()
        fig_hr.add_trace(go.Scatter(
            x=hourly_mean["jam"], y=hourly_mean["suhu"],
            name="Suhu (°C)", line=dict(color="#ff6b35", width=2.5),
            fill="tozeroy", fillcolor="rgba(255,107,53,0.08)"
        ))
        fig_hr.update_layout(
            paper_bgcolor="#04080f", plot_bgcolor="#0b1420",
            font=dict(family="Space Mono", color="#6b8aaa", size=11),
            xaxis=dict(title="Jam ke-", gridcolor="rgba(0,180,255,0.06)",
                       tickmode="linear", dtick=1),
            yaxis=dict(title="Suhu Rata-rata (°C)", gridcolor="rgba(0,180,255,0.06)"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            height=300, margin=dict(t=20, b=40, l=60, r=20),
        )
        st.plotly_chart(fig_hr, use_container_width=True)

    # Korelasi
    st.markdown("#### 🔗 Korelasi Antar Parameter")
    num_cols = [c for c in ["suhu", "hujan", "angin", "lembap"] if c in df.columns]
    if len(num_cols) >= 2:
        corr = df[num_cols].corr().round(2)
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[[0, "#0b1420"], [0.5, "#00b4ff"], [1, "#00ffc8"]],
            text=corr.values.round(2),
            texttemplate="%{text}",
            showscale=True,
            zmin=-1, zmax=1,
        ))
        fig_corr.update_layout(
            paper_bgcolor="#04080f", plot_bgcolor="#0b1420",
            font=dict(family="Space Mono", color="#6b8aaa", size=11),
            height=300, margin=dict(t=20, b=40, l=80, r=20),
        )
        st.plotly_chart(fig_corr, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN: LAPORAN PER JAM
# ═══════════════════════════════════════════════════════════════════════════════
elif "Laporan Per Jam" in page:
    st.markdown("## 📋 Laporan Agregasi Data Per Jam")
    st.markdown("Data mentah yang telah diagregasi per jam dari 6 file sumber meteorologi.")
    st.markdown("---")

    # Pilih hari
    if "tanggal" in df.columns:
        available_dates = sorted(df["tanggal"].dt.date.unique(), reverse=True)
        selected_date = st.selectbox("Pilih Tanggal", available_dates)
        df_hari = df[df["tanggal"].dt.date == selected_date].copy()
    else:
        df_hari = df.copy()

    df_laporan = get_hourly_aggregation(df_hari)

    # Tabel dengan conditional formatting
    st.markdown("#### 📊 Tabel Agregasi Per Jam")

    def color_status(val):
        colors = {
            "Ekstrim":  "background-color:rgba(255,85,85,0.15); color:#ff5555;",
            "Hujan":    "background-color:rgba(74,158,255,0.12); color:#4a9eff;",
            "Kabut":    "background-color:rgba(255,184,0,0.1); color:#ffb800;",
            "Normal":   "background-color:rgba(0,255,200,0.08); color:#00ffc8;",
        }
        return colors.get(val, "")

    def color_suhu(val):
        try:
            v = float(val)
            if v >= 35: return "color:#ff5555;"
            if v >= 33: return "color:#ff6b35;"
            if v >= 30: return "color:#ffb800;"
            return "color:#00ffc8;"
        except: return ""

    if not df_laporan.empty:
        display_df = df_laporan.copy()
        display_cols = {
            "jam_label":    "Jam",
            "suhu_avg":     "Suhu Avg (°C)",
            "suhu_min":     "Suhu Min",
            "suhu_max":     "Suhu Max",
            "hujan_total":  "Hujan (mm)",
            "angin_avg":    "Angin Avg",
            "angin_max":    "Angin Max",
            "lembap_avg":   "Kelembapan (%)",
            "status":       "Status",
        }
        display_df = display_df.rename(columns=display_cols)
        st.dataframe(
            display_df[[c for c in display_cols.values() if c in display_df.columns]]
                .style.applymap(color_suhu, subset=["Suhu Avg (°C)"] if "Suhu Avg (°C)" in display_df.columns else [])
                .applymap(color_status, subset=["Status"] if "Status" in display_df.columns else [])
                .format({
                    "Suhu Avg (°C)": "{:.1f}",
                    "Suhu Min": "{:.1f}",
                    "Suhu Max": "{:.1f}",
                    "Hujan (mm)": "{:.1f}",
                    "Angin Avg": "{:.1f}",
                    "Angin Max": "{:.1f}",
                    "Kelembapan (%)": "{:.0f}",
                }),
            use_container_width=True, height=500
        )

        # Download
        st.download_button(
            label="⬇️ Download CSV",
            data=df_laporan.to_csv(index=False, encoding="utf-8-sig"),
            file_name=f"laporan_bmkg_juanda_{selected_date if 'tanggal' in df.columns else 'all'}.csv",
            mime="text/csv",
        )
    else:
        st.info("Tidak ada data untuk tanggal yang dipilih.")


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN: PENGATURAN DATA
# ═══════════════════════════════════════════════════════════════════════════════
elif "Pengaturan Data" in page:
    st.markdown("## ⚙️ Pengaturan & Info Dataset")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📁 Status File Sumber")
        file_info = []
        for f in (df_raw["file_sumber"].unique() if "file_sumber" in df_raw.columns else ["Sample Data"]):
            rows = len(df_raw[df_raw["file_sumber"] == f]) if "file_sumber" in df_raw.columns else len(df_raw)
            file_info.append({"File": f, "Baris Data": rows, "Status": "✅ Loaded"})
        st.dataframe(pd.DataFrame(file_info), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### 📐 Ringkasan Dataset")
        st.markdown(f"""
        <div class='kpi-card' style='text-align:left;'>
            <div style='font-family:Space Mono,monospace; font-size:11px; color:#6b8aaa; line-height:2;'>
                Total Baris Data: <strong style='color:#00b4ff;'>{len(df_raw):,}</strong><br>
                Rentang Tanggal: <strong style='color:#00ffc8;'>
                    {df_raw['tanggal'].min().date() if 'tanggal' in df_raw.columns else '-'} –
                    {df_raw['tanggal'].max().date() if 'tanggal' in df_raw.columns else '-'}
                </strong><br>
                Kolom Tersedia: <strong style='color:#ff6b35;'>{', '.join(df_raw.columns[:8])}</strong><br>
                File Sumber: <strong style='color:#00b4ff;'>
                    {df_raw['file_sumber'].nunique() if 'file_sumber' in df_raw.columns else 1} file
                </strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📤 Upload File Baru")
    uploaded = st.file_uploader(
        "Upload file CSV atau Excel (format BMKG)",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )
    if uploaded:
        for f in uploaded:
            st.success(f"✅ {f.name} berhasil diupload ({f.size // 1024} KB)")
        st.info("💡 Restart aplikasi untuk memuat data baru ke dashboard.")

    st.markdown("#### 📝 Dokumentasi Format Data")
    st.markdown("""
    | Kolom | Tipe | Keterangan |
    |-------|------|-----------|
    | `tanggal` | date | Format YYYY-MM-DD |
    | `jam` | int | 0 – 23 |
    | `suhu` | float | Suhu udara (°C) |
    | `hujan` | float | Curah hujan (mm/jam) |
    | `angin` | float | Kecepatan angin (km/h) |
    | `arah_angin` | string | N, NE, E, SE, S, SW, W, NW |
    | `lembap` | float | Kelembapan relatif (%) |
    | `visibilitas` | float | Jarak pandang (km) |
    | `status` | string | Normal / Hujan / Kabut / Ekstrim |
    """)
