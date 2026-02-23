"""
pages/4_ℹ️_Info_Dataset.py
Informasi lengkap dataset, preview data mentah, statistik file
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Info Dataset – BMKG", page_icon="ℹ️", layout="wide")

from app import inject_css
inject_css()

if "df" not in st.session_state:
    st.error("⚠️ Data belum dimuat.")
    st.stop()

df   = st.session_state["df"]
df_h = st.session_state["df_hourly"]

FILES = [
    "/mnt/user-data/uploads/1771813453504_from_2025-02-01_to_2025-02-28.xlsx",
    "/mnt/user-data/uploads/1771813453505_from_2025-03-01_to_2025-03-31.xlsx",
    "/mnt/user-data/uploads/1771813453505_from_2025-04-01_to_2025-04-30.xlsx",
    "/mnt/user-data/uploads/1771813453506_from_2025-05-01_to_2025-05-31.xlsx",
    "/mnt/user-data/uploads/1771813453506_from_2025-06-01_to_2025-06-30.xlsx",
]

st.markdown("""
<h1 style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;color:#e2edf8;margin:0;'>
    ℹ️ Info Dataset & Sumber Data
</h1>
<p style='font-family:Space Mono,monospace;font-size:10px;color:#6b8aaa;margin:4px 0 16px;
text-transform:uppercase;letter-spacing:1px;'>
    5 File Excel BMKG Juanda · Feb–Jun 2025 · Data per menit UTC
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Ringkasan ─────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 📁 Status File Sumber")
    finfo = []
    for f in FILES:
        name = os.path.basename(f)
        size_mb = os.path.getsize(f) / 1024 / 1024 if os.path.exists(f) else 0
        rows = len(df[df["file_sumber"]==name]) if "file_sumber" in df.columns else 0
        finfo.append({
            "File": name.replace("1771813453504_","").replace("1771813453505_","").replace("1771813453506_",""),
            "Ukuran": f"{size_mb:.1f} MB",
            "Baris Data": f"{rows:,}",
            "Status": "✅ Loaded" if rows > 0 else "❌ Tidak Ada",
        })
    st.dataframe(pd.DataFrame(finfo), use_container_width=True, hide_index=True)

with c2:
    st.markdown("#### 📐 Ringkasan Dataset Gabungan")
    tgl_min = df["datetime"].min().strftime("%d %b %Y") if "datetime" in df.columns else "-"
    tgl_max = df["datetime"].max().strftime("%d %b %Y") if "datetime" in df.columns else "-"
    st.markdown(f"""
    <div class='kpi-card' style='text-align:left;line-height:2.2;'>
        <div style='font-family:Space Mono,monospace;font-size:12px;color:#6b8aaa;'>
            Total baris (menit): <strong style='color:#00b4ff;'>{len(df):,}</strong><br>
            Total baris (jam-an): <strong style='color:#00ffc8;'>{len(df_h):,}</strong><br>
            Periode: <strong style='color:#e2edf8;'>{tgl_min} – {tgl_max}</strong><br>
            Jumlah kolom asli: <strong style='color:#ff6b35;'>43 kolom</strong><br>
            File sumber: <strong style='color:#00b4ff;'>{df["file_sumber"].nunique() if "file_sumber" in df.columns else 5} file</strong><br>
            Resolusi asli: <strong style='color:#ffb800;'>1 menit (UTC)</strong><br>
            Resolusi output: <strong style='color:#ffb800;'>1 jam (agregasi)</strong>
        </div>
    </div>""", unsafe_allow_html=True)

# ── Statistik per file ─────────────────────────────────────────────────────────
st.markdown("#### 📊 Statistik Per Bulan")
if "file_sumber" in df.columns and "suhu" in df.columns:
    monthly_stat = df.groupby("file_sumber").agg(
        Baris=("suhu","count"),
        Suhu_Avg=("suhu","mean"),
        Suhu_Max=("suhu","max"),
        Suhu_Min=("suhu","min"),
        Hujan_Total=("hujan_1h","sum"),
        Angin_Max=("angin_kmh","max"),
        Lembap_Avg=("lembap","mean"),
    ).round(2).reset_index()
    monthly_stat.columns = ["File","Baris","Suhu Avg","Suhu Max","Suhu Min",
                             "Hujan Total (mm)","Angin Max (km/h)","Lembap Avg (%)"]
    monthly_stat["File"] = monthly_stat["File"].str.replace(
        r"^from_","", regex=True).str.replace(".xlsx","")
    st.dataframe(monthly_stat.style.background_gradient(cmap="Blues",
        subset=["Suhu Avg","Hujan Total (mm)","Angin Max (km/h)"],axis=0).format("{:.2f}",
        subset=["Suhu Avg","Suhu Max","Suhu Min","Hujan Total (mm)","Angin Max (km/h)","Lembap Avg (%)"]),
        use_container_width=True, hide_index=True)

# ── Preview data mentah ────────────────────────────────────────────────────────
st.markdown("#### 👁️ Preview Data Mentah")
preview_cols = [c for c in ["datetime","suhu","lembap","angin_kmh","arah_angin",
                              "hujan_1h","tekanan","radiasi","status","file_sumber"] if c in df.columns]
st.dataframe(df[preview_cols].head(100).style.format({
    "suhu":"{:.1f}","lembap":"{:.1f}","angin_kmh":"{:.1f}","hujan_1h":"{:.2f}",
    "tekanan":"{:.1f}","radiasi":"{:.0f}"}, na_rep="-"),
    use_container_width=True, height=400)

# ── Daftar kolom ──────────────────────────────────────────────────────────────
with st.expander("📋 Daftar Lengkap 43 Kolom File Asli"):
    st.markdown("""
    | # | Kolom Asli | Kolom Standar | Satuan |
    |---|-----------|--------------|--------|
    | 1 | time (UTC) | datetime | — |
    | 2 | Temperature Average 1 min | suhu | °C |
    | 3 | Temperature Average 10 min | — | °C |
    | 4 | Humidity Average 1 min | lembap | % |
    | 5 | Dew Point Average 1 min | dew_point | °C |
    | 6 | Wetbulb Temperature Average 1 min | — | °C |
    | 7 | Temperature Maximum 10 min | suhu_max_10m | °C |
    | 8 | Temperature Maximum 1 day | suhu_max_day | °C |
    | 9 | Temperature Minimum 10 min | suhu_min_10m | °C |
    | 10 | Temperature Minimum 1 day | suhu_min_day | °C |
    | 11 | Temperature Average 1 day | suhu_avg_day | °C |
    | 12 | Wind Direction Prevailing 1 min | arah_angin_deg | deg |
    | 13 | Wind Direction Prevailing 10 min | — | deg |
    | 14 | Wind Speed Average 1 min | angin_ms → angin_kmh | m/s → km/h |
    | 15 | Wind Speed Average 10 min | — | m/s |
    | 16 | Wind Speed Maximum 1 min | angin_max_ms → angin_max_kmh | m/s → km/h |
    | 17 | Wind Speed Maximum 10 min | — | m/s |
    | 18 | Wind Speed Minimum 1 min | angin_min_ms | m/s |
    | 19 | Accumulated Precipitation 1 hour | hujan_1h | mm |
    | 20 | Accumulated Precipitation 1 day | hujan_1day | mm |
    | 21 | Solar Radiation Average 1 min | radiasi | W/m² |
    | 22 | Total Solar Radiation 1 day | — | J/cm² |
    | 23 | Sunshine Duration 1 day | sunshine_h | jam |
    | 24 | Pressure Average 1 min | tekanan | mb |
    | 25 | QNH Average 1 min | qnh | mb |
    | 26 | QFE Average 1 min | — | mb |
    | 27 | QFF Average 1 min | — | mb |
    | 28 | Pressure Difference 3/12/1 day | — | mb |
    | 29 | Evaporation 1 day | — | mm |
    | 30 | Water Level Average 1 min | water_level | mm |
    | 31 | Water Temperature Average 1 min | suhu_air | °C |
    | 32 | Wind Evaporation Average 1 min | — | m/s |
    | ... | dst. | | |
    """)
