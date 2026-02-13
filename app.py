import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

st.set_page_config(page_title="BMKG Juanda Dashboard", layout="wide")
st.title("🌦️ Dashboard Monitoring Cuaca BMKG Juanda (Per Bulan)")

# 1) List file bulanan
files = sorted(glob.glob("bmkg_hourly.csv"))
if not files:
    st.error("Folder data/ kosong. Upload file CSV bulanan ke folder data/ di repo GitHub.")
    st.stop()

# bikin label yang enak dibaca
options = {os.path.basename(f): f for f in files}

selected_name = st.sidebar.selectbox(
    "Pilih bulan data",
    list(options.keys())
)
selected_file = options[selected_name]

st.sidebar.caption(f"File dipilih: {selected_name}")

@st.cache_data(show_spinner=True)
def load_and_aggregate(path: str) -> pd.DataFrame:
    # CSV kamu dari Excel pakai delimiter ; dan encoding cp1252
    df = pd.read_csv(path, encoding="cp1252", sep=";")
    df.columns = [c.replace(";", "").strip() for c in df.columns]

    # kolom waktu valid adalah 'time (UTC)'
    df["time (UTC)"] = pd.to_datetime(df["time (UTC)"], errors="coerce")
    df = df.dropna(subset=["time (UTC)"]).set_index("time (UTC)").sort_index()

    # agregasi per jam
    hourly = df.resample("1H").mean(numeric_only=True)

    # curah hujan 1 jam: ambil nilai terakhir dalam jam tsb (lebih masuk akal daripada mean)
    rain_col = "Accumulated Precipitation 1 hour (mm)"
    if rain_col in df.columns:
        hourly[rain_col] = df[rain_col].resample("1H").last()

    hourly = hourly.reset_index().rename(columns={"time (UTC)": "timestamp"})
    return hourly

# 2) Load hanya 1 bulan
hourly = load_and_aggregate(selected_file)

# 3) Filter tanggal (optional, dalam 1 bulan pun bisa)
hourly["timestamp"] = pd.to_datetime(hourly["timestamp"])
min_date = hourly["timestamp"].min().date()
max_date = hourly["timestamp"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Rentang tanggal (opsional)",
    [min_date, max_date]
)

mask = (hourly["timestamp"].dt.date >= start_date) & (hourly["timestamp"].dt.date <= end_date)
dff = hourly.loc[mask].copy()

# 4) Pilih parameter untuk grafik
num_cols = dff.select_dtypes("number").columns.tolist()
if not num_cols:
    st.warning("Tidak ada kolom numerik untuk diplot.")
    st.stop()

parameter = st.sidebar.selectbox("Pilih parameter", num_cols)

# Ringkasan cepat
c1, c2, c3 = st.columns(3)
c1.metric("Jumlah jam", len(dff))
c2.metric("Maks", float(dff[parameter].max()))
c3.metric("Min", float(dff[parameter].min()))

# Grafik
fig = px.line(dff, x="timestamp", y=parameter, title=f"{parameter} (Per Jam)")
st.plotly_chart(fig, use_container_width=True)

with st.expander("Lihat data agregasi per jam"):
    st.dataframe(dff, use_container_width=True)
