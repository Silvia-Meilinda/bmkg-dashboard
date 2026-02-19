import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard BMKG Juanda", layout="wide")

st.title("Dashboard Monitoring Data Meteorologi (Per Jam)")

df = pd.read_csv("bmkg_hourly.csv")
df["time"] = pd.to_datetime(df["time (UTC)"])

# Filter tanggal
min_date = df["time"].min().date()
max_date = df["time"].max().date()

start_date, end_date = st.date_input(
    "Pilih Rentang Tanggal",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

mask = (df["time"].dt.date >= start_date) & (df["time"].dt.date <= end_date)
filtered = df.loc[mask]

st.subheader("Grafik Tren Per Jam")

columns = [
    "Temperature Average 1 min (oC);",
    "Humidity Average 1 min (%);",
    "Wind Speed Average 1 min (m/s);"
]

available_cols = [c for c in columns if c in filtered.columns]

if available_cols:
    st.line_chart(filtered.set_index("time")[available_cols])

st.subheader("Data Detail")
st.dataframe(filtered)
st.subheader("Ringkasan Indikator")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Rata-rata Suhu (°C)", round(filtered["Temperature Average 1 min (oC);"].mean(), 2))
col2.metric("Rata-rata Kelembapan (%)", round(filtered["Humidity Average 1 min (%);"].mean(), 2))
col3.metric("Kecepatan Angin Maks (m/s)", round(filtered["Wind Speed Maximum 10 min (m/s);"].max(), 2))
col4.metric("Total Curah Hujan (mm)", round(filtered["Accumulated Precipitation 1 hour (mm);"].sum(), 2))
st.subheader("Analisis Otomatis")

if filtered["Temperature Average 1 min (oC);"].mean() > 33:
    st.warning("Suhu rata-rata tinggi. Potensi heat stress meningkat.")

if filtered["Accumulated Precipitation 1 hour (mm);"].sum() > 50:
    st.warning("Curah hujan tinggi dalam periode ini. Potensi genangan.")

st.subheader("Analisis Jam Puncak")

peak_hour = filtered.groupby(filtered["time"].dt.hour)["Temperature Average 1 min (oC);"].mean().idxmax()

st.info(f"Suhu rata-rata tertinggi terjadi sekitar pukul {peak_hour}:00")

daily_rain = filtered.resample("D", on="time")["Accumulated Precipitation 1 hour (mm);"].sum()

if daily_rain.max() > 50:
    st.warning("Terdapat hari dengan curah hujan tinggi (>50 mm).")
st.download_button(
    label="Download Data Filtered",
    data=filtered.to_csv(index=False),
    file_name="laporan_bmkg_filtered.csv",
    mime="text/csv"
)
