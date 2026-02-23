"""
Script untuk generate file CSV demo di folder data/
Jalankan sekali: python generate_demo_data.py
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

os.makedirs("data", exist_ok=True)
np.random.seed(42)

arah_options = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
file_months  = [
    ("Data_BMKG_Jan2025.csv",  datetime(2025, 1, 1), 31),
    ("Data_BMKG_Feb2025.csv",  datetime(2025, 2, 1), 28),
    ("Data_BMKG_Mar2025.csv",  datetime(2025, 3, 1), 31),
    ("Data_BMKG_Apr2025.csv",  datetime(2025, 4, 1), 30),
    ("Data_BMKG_May2025.csv",  datetime(2025, 5, 1), 31),
    ("Data_BMKG_Jun2025.csv",  datetime(2025, 6, 1), 30),
]

for filename, base_date, n_days in file_months:
    records = []
    for day in range(n_days):
        tanggal = base_date + timedelta(days=day)
        for jam in range(24):
            suhu = 27 + 7 * np.sin(np.pi * (jam - 6) / 12) if 6 <= jam <= 18 else 27
            suhu += np.random.normal(0, 0.8)
            suhu  = round(max(23, min(37, suhu)), 1)

            hujan = max(0, np.random.exponential(4 if 12 <= jam <= 17 else 0.3))
            hujan = round(hujan if np.random.random() < 0.4 else 0.0, 1)

            angin = round(max(2, 12 + np.random.exponential(5) + (4 if 10 <= jam <= 16 else 0)), 1)
            angin_max = round(angin * (1.2 + np.random.random() * 0.5), 1)
            arah  = np.random.choice(arah_options, p=[0.2, 0.1, 0.1, 0.05, 0.1, 0.1, 0.2, 0.15])

            lembap = round(max(50, min(99, 92 - (suhu - 25) * 1.2 + np.random.normal(0, 3))), 1)
            vis    = round(max(1, 9 - hujan * 0.25 + np.random.normal(0, 0.8)), 1)

            if hujan >= 20 or angin > 40:   status = "Ekstrim"
            elif hujan >= 5:                 status = "Hujan"
            elif lembap >= 93:               status = "Kabut"
            else:                            status = "Normal"

            records.append({
                "Tanggal":     tanggal.strftime("%Y-%m-%d"),
                "Jam":         jam,
                "Suhu":        suhu,
                "RR":          hujan,
                "FF":          angin,
                "FF_Max":      angin_max,
                "DD":          arah,
                "RH":          lembap,
                "VV":          vis,
                "Status":      status,
            })

    df = pd.DataFrame(records)
    path = os.path.join("data", filename)
    df.to_csv(path, index=False)
    print(f"✅ {filename} → {len(df)} baris")

print("\n✔ Semua file demo berhasil dibuat di folder data/")
