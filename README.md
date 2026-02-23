# 🌤 BMKG Juanda — Dashboard Analitik Data Cuaca

Dashboard monitoring internal untuk analisis data meteorologi BMKG Juanda dengan agregasi per jam.

---

## 📁 Struktur Repository

```
bmkg-dashboard/
│
├── app.py                          # ← File utama Streamlit
├── requirements.txt                # ← Library yang dibutuhkan
├── README.md
│
├── .streamlit/
│   └── config.toml                 # ← Konfigurasi tema & server
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py              # ← Load & agregasi data CSV/Excel
│   ├── charts.py                   # ← Semua chart Plotly
│   ├── insights.py                 # ← Generate insight & rekomendasi otomatis
│   └── helpers.py                  # ← Fungsi bantuan umum
│
└── data/                           # ← Letakkan file CSV/Excel di sini
    ├── Data_BMKG_01.csv
    ├── Data_BMKG_02.csv
    └── ... (6 file)
```

---

## 🚀 Cara Menjalankan

### 1. Clone / Download Repository

```bash
git clone https://github.com/username/bmkg-dashboard.git
cd bmkg-dashboard
```

### 2. Buat Virtual Environment (Rekomendasi)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Siapkan Data

Letakkan file CSV atau Excel BMKG di folder `data/`:

```
data/
├── Data_Jan_2025.csv
├── Data_Feb_2025.csv
└── ...
```

Format kolom yang didukung (nama bisa bervariasi, sistem akan otomatis mendeteksi):

| Kolom       | Tipe   | Keterangan                    |
|-------------|--------|-------------------------------|
| `tanggal`   | date   | Format YYYY-MM-DD             |
| `jam`       | int    | 0 – 23                        |
| `suhu`      | float  | Suhu udara (°C)               |
| `hujan`     | float  | Curah hujan (mm/jam)          |
| `angin`     | float  | Kecepatan angin (km/h)        |
| `arah_angin`| string | N, NE, E, SE, S, SW, W, NW   |
| `lembap`    | float  | Kelembapan relatif (%)        |
| `visibilitas`| float | Jarak pandang (km)            |
| `status`    | string | Normal/Hujan/Kabut/Ekstrim    |

> ℹ️ Jika folder `data/` kosong, dashboard akan otomatis menggunakan **data demo** selama 30 hari.

### 5. Jalankan Dashboard

```bash
streamlit run app.py
```

Buka browser: **http://localhost:8501**

---

## 📊 Fitur Dashboard

| Fitur | Keterangan |
|-------|-----------|
| **Dashboard Utama** | KPI cards, tren per jam, heatmap, insight & rekomendasi |
| **Analisis Tren** | Multi-parameter chart, statistik deskriptif, korelasi |
| **Laporan Per Jam** | Tabel agregasi per jam + export CSV |
| **Pengaturan Data** | Upload file baru, info dataset, dokumentasi format |

### Visualisasi yang Tersedia

- 🌡️ Line chart tren suhu dengan min/max band
- 🌧️ Bar chart curah hujan per jam (color-coded intensitas)
- 💨 Wind Rose distribusi arah & kecepatan angin
- 🔥 Heatmap intensitas cuaca (jam × hari)
- 📈 Multi-parameter chart dengan dual axis
- 🔗 Correlation heatmap antar parameter

### Insight & Rekomendasi Otomatis

Sistem menganalisis data dan menghasilkan:
- ⚠️ Peringatan cuaca ekstrim
- 📊 Pola tren (suhu, hujan, angin)
- ✅ Rekomendasi operasional (personel, penerbangan, notifikasi)

---

## ⚙️ Konfigurasi

Edit threshold peringatan di sidebar:
- **Suhu Ekstrim**: default 35°C
- **Hujan Lebat**: default 20 mm/jam
- **Angin Kencang**: default 40 km/h

---

## 🌍 SDGs

Mendukung **SDG 13 – Climate Action** melalui sistem informasi analitik meteorologi untuk pengambilan keputusan operasional BMKG Juanda.

---

## 📋 Requirements

```
streamlit==1.35.0
pandas==2.2.2
numpy==1.26.4
plotly==5.22.0
openpyxl==3.1.2
xlrd==2.0.1
pytz==2024.1
```

---

## 👤 Pengembang

Dikembangkan sebagai proyek skripsi — Manajemen Sistem Informasi  
Topik: *Dashboard Analitik Data Cuaca BMKG Juanda dengan Agregasi Per Jam untuk Mendukung Layanan Internal*
