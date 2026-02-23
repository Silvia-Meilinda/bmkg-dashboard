"""
pages/2_📈_Analisis_Tren.py
Halaman analisis tren mendalam: statistik, korelasi, distribusi, perbandingan bulan
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Analisis Tren – BMKG", page_icon="📈", layout="wide")

from app import inject_css
inject_css()

from utils.charts import make_multi_param_chart, make_histogram, make_daily_trend

if "df" not in st.session_state:
    st.error("⚠️ Data belum dimuat.")
    st.stop()

df   = st.session_state["df"]
df_h = st.session_state["df_hourly"]
df_d = st.session_state.get("df_daily", pd.DataFrame())

BG, SURF, SURF2 = "#04080f", "#0b1420", "#111d2e"
GRID = "rgba(0,180,255,0.07)"
MUT, TXT = "#6b8aaa", "#e2edf8"

st.markdown("""
<h1 style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;color:#e2edf8;margin:0;'>
    📈 Analisis Tren Cuaca
</h1>
<p style='font-family:Space Mono,monospace;font-size:10px;color:#6b8aaa;margin:4px 0 16px;
text-transform:uppercase;letter-spacing:1px;'>
    Visualisasi mendalam · Statistik · Korelasi · Distribusi
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── 1. Multi-parameter per jam ────────────────────────────────────────────────
st.markdown("#### Parameter Gabungan Per Jam")
params = st.multiselect("Pilih Parameter",
    ["Suhu (°C)","Curah Hujan (mm)","Angin (km/h)","Kelembapan (%)","Tekanan (mb)","Radiasi (W/m2)"],
    default=["Suhu (°C)","Curah Hujan (mm)"])
if params:
    st.plotly_chart(make_multi_param_chart(df_h, params), use_container_width=True)

# ── 2. Tren Harian ────────────────────────────────────────────────────────────
if not df_d.empty:
    st.markdown("#### Tren Harian")
    d_param = st.selectbox("Parameter",
        {"suhu_avg":"Suhu Avg","hujan_total":"Curah Hujan","angin_avg":"Angin Avg",
         "angin_max":"Angin Max","lembap_avg":"Kelembapan"}.keys(),
        format_func={"suhu_avg":"Suhu Avg","hujan_total":"Curah Hujan","angin_avg":"Angin Avg",
                     "angin_max":"Angin Max","lembap_avg":"Kelembapan"}.get)
    st.plotly_chart(make_daily_trend(df_d, d_param), use_container_width=True)

# ── 3. Distribusi ─────────────────────────────────────────────────────────────
st.markdown("#### Distribusi Nilai")
dc1, dc2 = st.columns(2)
with dc1:
    st.plotly_chart(make_histogram(df, "suhu"), use_container_width=True)
with dc2:
    st.plotly_chart(make_histogram(df, "angin_kmh"), use_container_width=True)

dc3, dc4 = st.columns(2)
with dc3:
    st.plotly_chart(make_histogram(df, "lembap"), use_container_width=True)
with dc4:
    st.plotly_chart(make_histogram(df, "hujan_1h"), use_container_width=True)

# ── 4. Statistik deskriptif ───────────────────────────────────────────────────
st.markdown("#### 📐 Statistik Deskriptif Per Jam")
num_cols = [c for c in ["suhu_avg","suhu_min","suhu_max","hujan_total","angin_avg",
                         "angin_max","lembap_avg","tekanan_avg"] if c in df_h.columns]
col_labels = {"suhu_avg":"Suhu Avg","suhu_min":"Suhu Min","suhu_max":"Suhu Max",
               "hujan_total":"Hujan","angin_avg":"Angin Avg","angin_max":"Angin Max",
               "lembap_avg":"Kelembapan","tekanan_avg":"Tekanan"}
if num_cols:
    stat = df_h[num_cols].rename(columns=col_labels).describe().round(2)
    st.dataframe(stat.style.background_gradient(cmap="Blues",axis=None).format("{:.2f}"),
                 use_container_width=True)

# ── 5. Korelasi ───────────────────────────────────────────────────────────────
st.markdown("#### 🔗 Korelasi Antar Parameter")
if len(num_cols) >= 2:
    corr = df_h[num_cols].rename(columns=col_labels).corr().round(2)
    fig_c = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
        colorscale=[[0,SURF],[0.5,"#00b4ff"],[1,"#00ffc8"]],
        text=corr.values.round(2), texttemplate="%{text}",
        showscale=True, zmin=-1, zmax=1,
        hovertemplate="<b>%{x} × %{y}</b><br>r = %{z:.2f}<extra></extra>",
    ))
    fig_c.update_layout(
        paper_bgcolor=BG, plot_bgcolor=SURF,
        font=dict(family="Space Mono",color=MUT,size=11),
        height=360, margin=dict(t=20,b=40,l=100,r=20),
        hoverlabel=dict(bgcolor=SURF2,font=dict(family="Space Mono",color=TXT,size=11)),
    )
    st.plotly_chart(fig_c, use_container_width=True)

# ── 6. Perbandingan antar bulan ───────────────────────────────────────────────
st.markdown("#### 📅 Perbandingan Rata-rata Per Bulan")
if "nama_bulan" in df.columns and "suhu" in df.columns:
    monthly = df.groupby("nama_bulan").agg(
        suhu_avg=("suhu","mean"),
        hujan_sum=("hujan_1h","sum"),
        angin_avg=("angin_kmh","mean"),
    ).round(2).reset_index()

    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(x=monthly["nama_bulan"], y=monthly["suhu_avg"],
        name="Suhu Avg (°C)", marker_color="rgba(255,107,53,0.7)"))
    fig_m.add_trace(go.Bar(x=monthly["nama_bulan"], y=monthly["angin_avg"],
        name="Angin Avg (km/h)", marker_color="rgba(0,255,200,0.6)"))
    fig_m.update_layout(
        paper_bgcolor=BG, plot_bgcolor=SURF, barmode="group",
        font=dict(family="Space Mono",color=MUT,size=11),
        height=300, margin=dict(t=20,b=40,l=60,r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=TXT)),
        hoverlabel=dict(bgcolor=SURF2,font=dict(family="Space Mono",color=TXT,size=11)),
        xaxis=dict(gridcolor=GRID), yaxis=dict(gridcolor=GRID),
    )
    st.plotly_chart(fig_m, use_container_width=True)
