"""
utils/data_loader.py
Modul untuk memuat dan mengagregasi data meteorologi BMKG Juanda
"""

import os
import glob
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# ── Kolom yang diharapkan dari file BMKG ──────────────────────────────────────
EXPECTED_COLS = {
    # nama variasi   → nama standar
    "Tanggal":       "tanggal",
    "DATE":          "tanggal",
    "Date":          "tanggal",
    "TGL":           "tanggal",
    "Jam":           "jam",
    "JAM":           "jam",
    "Hour":          "jam",
    "Suhu":          "suhu",
    "SUHU":          "suhu",
    "Temp":          "suhu",
    "Temperature":   "suhu",
    "RR":            "hujan",
    "Hujan":         "hujan",
    "Rainfall":      "hujan",
    "CH":            "hujan",
    "FF":            "angin",
    "Angin":         "angin",
    "Wind Speed":    "angin",
    "Windspeed":     "angin",
    "DD":            "arah_angin",
    "Arah Angin":    "arah_angin",
    "Wind Dir":      "arah_angin",
    "RH":            "lembap",
    "Lembap":        "lembap",
    "Humidity":      "lembap",
    "VV":            "visibilitas",
    "Visibilitas":   "visibilitas",
    "Visibility":    "visibilitas",
    "Status":        "status",
    "Cuaca":         "status",
    "Weather":       "status",
}


def load_csv_file(filepath: str) -> pd.DataFrame:
    """Baca satu file CSV dengan deteksi separator otomatis."""
    for sep in [",", ";", "\t"]:
        try:
            df = pd.read_csv(filepath, sep=sep, encoding="utf-8", low_memory=False)
            if len(df.columns) > 2:
                return df
        except Exception:
            pass
    try:
        return pd.read_csv(filepath, encoding="latin-1", low_memory=False)
    except Exception as e:
        print(f"[WARN] Gagal baca {filepath}: {e}")
        return pd.DataFrame()


def load_excel_file(filepath: str) -> pd.DataFrame:
    """Baca file Excel."""
    try:
        return pd.read_excel(filepath, engine="openpyxl")
    except Exception:
        try:
            return pd.read_excel(filepath, engine="xlrd")
        except Exception as e:
            print(f"[WARN] Gagal baca {filepath}: {e}")
            return pd.DataFrame()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename kolom ke format standar."""
    rename_map = {}
    for col in df.columns:
        col_str = str(col).strip()
        if col_str in EXPECTED_COLS:
            rename_map[col] = EXPECTED_COLS[col_str]
        else:
            # coba case-insensitive match
            for key, val in EXPECTED_COLS.items():
                if col_str.lower() == key.lower():
                    rename_map[col] = val
                    break
    return df.rename(columns=rename_map)


def parse_tanggal(df: pd.DataFrame) -> pd.DataFrame:
    """Parsing kolom tanggal ke datetime."""
    if "tanggal" not in df.columns:
        return df
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
               "%d %B %Y", "%d-%b-%Y", "%Y%m%d"]
    for fmt in formats:
        try:
            df["tanggal"] = pd.to_datetime(df["tanggal"], format=fmt, errors="coerce")
            if df["tanggal"].notna().sum() > len(df) * 0.5:
                break
        except Exception:
            pass
    if df["tanggal"].dtype == "object":
        df["tanggal"] = pd.to_datetime(df["tanggal"], infer_datetime_format=True, errors="coerce")
    return df


def parse_jam(df: pd.DataFrame) -> pd.DataFrame:
    """Pastikan kolom jam berupa integer 0-23."""
    if "jam" not in df.columns:
        if "tanggal" in df.columns and pd.api.types.is_datetime64_any_dtype(df["tanggal"]):
            df["jam"] = df["tanggal"].dt.hour
        else:
            df["jam"] = 0
        return df

    # Kalau jam dalam format "07:00" atau "07.00"
    if df["jam"].dtype == "object":
        df["jam"] = df["jam"].astype(str).str.extract(r"(\d{1,2})")[0].astype(float).astype(int)
    else:
        df["jam"] = pd.to_numeric(df["jam"], errors="coerce").fillna(0).astype(int)

    df["jam"] = df["jam"].clip(0, 23)
    return df


def clean_numeric(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Bersihkan kolom numerik: hapus satuan, konversi, isi NaN."""
    for col in cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(r"[^\d.\-]", "", regex=True)
                .replace("", np.nan)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Imputasi NaN dengan median
    for col in cols:
        if col in df.columns:
            median = df[col].median()
            df[col] = df[col].fillna(median if pd.notna(median) else 0)
    return df


def derive_status(df: pd.DataFrame) -> pd.DataFrame:
    """Derive kolom status jika belum ada."""
    if "status" not in df.columns:
        cond = [
            (df["hujan"] >= 20) if "hujan" in df.columns else pd.Series(False, index=df.index),
            (df["hujan"] >= 5)  if "hujan" in df.columns else pd.Series(False, index=df.index),
            (df["lembap"] >= 95) if "lembap" in df.columns else pd.Series(False, index=df.index),
        ]
        choices = ["Ekstrim", "Hujan", "Kabut"]
        default = "Normal"
        df["status"] = np.select(cond, choices, default=default)
    return df


def load_single_file(filepath: str) -> pd.DataFrame:
    """Load satu file (CSV / XLSX) dan standardisasi."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".xlsx", ".xls"]:
        df = load_excel_file(filepath)
    else:
        df = load_csv_file(filepath)

    if df.empty:
        return df

    df = standardize_columns(df)
    df = parse_tanggal(df)
    df = parse_jam(df)
    df = clean_numeric(df, ["suhu", "hujan", "angin", "lembap", "visibilitas"])
    df = derive_status(df)
    df["file_sumber"] = os.path.basename(filepath)
    return df


def load_all_data(data_dir: str = "data/") -> pd.DataFrame:
    """
    Load semua file CSV dan Excel dari folder data/.
    Jika folder kosong atau tidak ada, kembalikan data dummy.
    """
    files = (
        glob.glob(os.path.join(data_dir, "*.csv"))
        + glob.glob(os.path.join(data_dir, "*.xlsx"))
        + glob.glob(os.path.join(data_dir, "*.xls"))
    )

    frames = []
    for f in files:
        df = load_single_file(f)
        if not df.empty:
            frames.append(df)
            print(f"[INFO] Loaded: {f} → {len(df)} baris")

    if frames:
        return pd.concat(frames, ignore_index=True)

    # ── Jika tidak ada file → gunakan data demo ──────────────────────────────
    print("[INFO] Tidak ada file di folder data/, menggunakan data demo.")
    return generate_demo_data()


def generate_demo_data() -> pd.DataFrame:
    """
    Generate data demo realistis 30 hari untuk keperluan demo/development.
    """
    np.random.seed(42)
    records = []
    base_date = datetime.now() - timedelta(days=30)
    files = [f"Data_BMKG_{i+1:02d}.csv" for i in range(6)]

    for day_offset in range(30):
        tanggal = base_date + timedelta(days=day_offset)
        file_src = files[day_offset % len(files)]

        for jam in range(24):
            # Suhu: rendah pagi, puncak siang, turun malam
            suhu_base = 27 + 8 * np.sin(np.pi * (jam - 6) / 12) if 6 <= jam <= 18 else 27
            suhu = suhu_base + np.random.normal(0, 0.8)
            suhu = max(24, min(38, suhu))

            # Hujan: lebih tinggi sore hari (12–18)
            hujan_base = 5 if 12 <= jam <= 18 else 0.5
            hujan = max(0, np.random.exponential(hujan_base) * (0.3 + np.random.random()))
            if np.random.random() > 0.35:
                hujan = 0.0

            # Angin
            angin = 10 + np.random.exponential(8) + (5 if 10 <= jam <= 16 else 0)
            angin = max(0, min(60, angin))
            angin_max = angin * (1.3 + np.random.random() * 0.4)

            # Kelembapan: berbanding terbalik dengan suhu
            lembap = 95 - (suhu - 24) * 1.5 + np.random.normal(0, 3)
            lembap = max(50, min(100, lembap))

            # Visibilitas
            visibilitas = max(1, 10 - hujan * 0.3 + np.random.normal(0, 1))

            # Arah angin
            arah_options = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            arah_angin = np.random.choice(arah_options, p=[0.2, 0.1, 0.1, 0.05, 0.1, 0.1, 0.2, 0.15])

            # Status
            if hujan >= 20 or angin > 40:
                status = "Ekstrim"
            elif hujan >= 5:
                status = "Hujan"
            elif lembap >= 93:
                status = "Kabut"
            else:
                status = "Normal"

            records.append({
                "tanggal":     tanggal,
                "jam":         jam,
                "suhu":        round(suhu, 1),
                "hujan":       round(hujan, 1),
                "angin":       round(angin, 1),
                "angin_max":   round(angin_max, 1),
                "arah_angin":  arah_angin,
                "lembap":      round(lembap, 1),
                "visibilitas": round(visibilitas, 1),
                "status":      status,
                "file_sumber": file_src,
            })

    return pd.DataFrame(records)


def get_hourly_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi data ke level per jam.
    Menghasilkan: rata-rata suhu, total hujan, max/min angin, dll.
    """
    if df.empty:
        return pd.DataFrame()

    agg_funcs = {}
    if "suhu"       in df.columns: agg_funcs["suhu_avg"]    = ("suhu",       "mean")
    if "suhu"       in df.columns: agg_funcs["suhu_min"]    = ("suhu",       "min")
    if "suhu"       in df.columns: agg_funcs["suhu_max"]    = ("suhu",       "max")
    if "hujan"      in df.columns: agg_funcs["hujan_total"] = ("hujan",      "sum")
    if "hujan"      in df.columns: agg_funcs["hujan_avg"]   = ("hujan",      "mean")
    if "angin"      in df.columns: agg_funcs["angin_avg"]   = ("angin",      "mean")
    if "angin_max"  in df.columns: agg_funcs["angin_max"]   = ("angin_max",  "max")
    elif "angin"    in df.columns: agg_funcs["angin_max"]   = ("angin",      "max")
    if "lembap"     in df.columns: agg_funcs["lembap_avg"]  = ("lembap",     "mean")
    if "visibilitas"in df.columns: agg_funcs["visibilitas"] = ("visibilitas","mean")

    group_cols = ["jam"]
    if "tanggal" in df.columns:
        df = df.copy()
        df["tanggal_date"] = pd.to_datetime(df["tanggal"]).dt.date
        group_cols = ["tanggal_date", "jam"]

    df_agg = df.groupby(group_cols).agg(**agg_funcs).reset_index()

    # Label jam
    df_agg["jam_label"] = df_agg["jam"].apply(lambda x: f"{int(x):02d}:00")

    # Status dominan
    if "status" in df.columns:
        status_mode = df.groupby(group_cols)["status"].agg(
            lambda x: x.mode()[0] if not x.empty else "Normal"
        ).reset_index()
        df_agg = df_agg.merge(status_mode, on=group_cols, how="left")

    # Round
    for col in ["suhu_avg", "suhu_min", "suhu_max", "angin_avg", "lembap_avg", "visibilitas"]:
        if col in df_agg.columns:
            df_agg[col] = df_agg[col].round(1)
    for col in ["hujan_total", "hujan_avg", "angin_max"]:
        if col in df_agg.columns:
            df_agg[col] = df_agg[col].round(1)

    return df_agg
