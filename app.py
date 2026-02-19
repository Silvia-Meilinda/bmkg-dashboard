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
