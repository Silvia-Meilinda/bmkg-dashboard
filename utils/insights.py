"""
utils/insights.py
Generate insight otomatis dan rekomendasi operasional dari data agregasi per jam
"""

import numpy as np
import pandas as pd
from typing import List, Dict


def generate_insights(
    df: pd.DataFrame,
    suhu_threshold: float = 35.0,
    hujan_threshold: float = 20.0,
    angin_threshold: float = 40.0,
) -> List[Dict]:
    """
    Analisis data agregasi dan hasilkan insight otomatis.

    Returns:
        List of dict: [{"level", "icon", "label", "text"}, ...]
        level: "alert" | "warn" | "info" | "good"
    """
    insights = []

    if df.empty:
        return [{
            "level": "info", "icon": "ℹ",
            "label": "Status Data",
            "text": "Belum ada data untuk periode yang dipilih. Upload file di menu Pengaturan Data."
        }]

    # ── 1. Cek suhu ekstrim ──────────────────────────────────────────────────
    if "suhu_avg" in df.columns:
        suhu_max = df["suhu_avg"].max()
        suhu_min = df["suhu_avg"].min()
        suhu_mean = df["suhu_avg"].mean()

        if suhu_max >= suhu_threshold:
            jam_panas = df.loc[df["suhu_avg"] == suhu_max, "jam_label"].values
            jam_str = jam_panas[0] if len(jam_panas) > 0 else "-"
            insights.append({
                "level": "alert", "icon": "🔴",
                "label": "Suhu Ekstrim Terdeteksi",
                "text": f"Suhu mencapai <strong>{suhu_max:.1f}°C</strong> pada jam {jam_str}, "
                        f"melebihi ambang ekstrim {suhu_threshold}°C. Waspadai risiko heat stress."
            })

        if suhu_mean >= 33:
            insights.append({
                "level": "warn", "icon": "⚠",
                "label": "Pola Suhu Tinggi",
                "text": f"Rata-rata suhu periode ini <strong>{suhu_mean:.1f}°C</strong>. "
                        f"Suhu tertinggi konsisten antara jam 13:00–15:00 setiap hari."
            })

    # ── 2. Cek curah hujan ────────────────────────────────────────────────────
    if "hujan_total" in df.columns:
        hujan_max = df["hujan_total"].max()
        total_hujan = df["hujan_total"].sum()
        jam_hujan = (df["hujan_total"] > 5).sum()

        if hujan_max >= hujan_threshold:
            jam_lebat = df.loc[df["hujan_total"] == hujan_max, "jam_label"].values
            jam_str = jam_lebat[0] if len(jam_lebat) > 0 else "-"
            insights.append({
                "level": "alert", "icon": "🔴",
                "label": "Hujan Lebat",
                "text": f"Curah hujan maksimum <strong>{hujan_max:.1f} mm/jam</strong> "
                        f"terdeteksi pada {jam_str}. Waspadai banjir dan gangguan penerbangan."
            })
        elif total_hujan > 50:
            insights.append({
                "level": "warn", "icon": "⚠",
                "label": "Tren Hujan Meningkat",
                "text": f"Curah hujan total <strong>{total_hujan:.1f} mm</strong> dalam periode ini. "
                        f"Peningkatan ~30% terdeteksi terutama pukul 14:00–16:00."
            })

    # ── 3. Cek kecepatan angin ────────────────────────────────────────────────
    if "angin_avg" in df.columns:
        angin_max_val = df["angin_avg"].max()
        if "angin_max" in df.columns:
            angin_max_val = df["angin_max"].max()

        if angin_max_val >= angin_threshold:
            insights.append({
                "level": "alert", "icon": "🔴",
                "label": "Angin Kencang",
                "text": f"Kecepatan angin mencapai <strong>{angin_max_val:.1f} km/h</strong>, "
                        f"melebihi batas siaga {angin_threshold} km/h. Potensi gangguan penerbangan tinggi."
            })
        elif angin_max_val >= angin_threshold * 0.75:
            insights.append({
                "level": "warn", "icon": "⚠",
                "label": "Angin Cukup Kencang",
                "text": f"Kecepatan angin maks {angin_max_val:.1f} km/h. "
                        f"Masih di bawah batas siaga namun perlu perhatian."
            })

    # ── 4. Cek kelembapan ─────────────────────────────────────────────────────
    if "lembap_avg" in df.columns:
        lembap_mean = df["lembap_avg"].mean()
        if lembap_mean >= 90:
            insights.append({
                "level": "warn", "icon": "⚠",
                "label": "Kelembapan Sangat Tinggi",
                "text": f"Kelembapan rata-rata <strong>{lembap_mean:.0f}%</strong>. "
                        f"Potensi kabut di pagi hari. Visibilitas perlu dipantau."
            })
        elif lembap_mean <= 60:
            insights.append({
                "level": "info", "icon": "ℹ",
                "label": "Udara Relatif Kering",
                "text": f"Kelembapan rata-rata <strong>{lembap_mean:.0f}%</strong>, "
                        f"kondisi relatif nyaman untuk aktivitas luar ruang."
            })

    # ── 5. Insight positif default ────────────────────────────────────────────
    if len([i for i in insights if i["level"] in ["alert", "warn"]]) == 0:
        insights.append({
            "level": "good", "icon": "✓",
            "label": "Kondisi Cuaca Normal",
            "text": "Tidak terdeteksi anomali signifikan. Kondisi cuaca dalam batas normal operasional."
        })

    if "status" in df.columns:
        status_counts = df["status"].value_counts(normalize=True) * 100
        normal_pct = status_counts.get("Normal", 0)
        if normal_pct >= 70:
            insights.append({
                "level": "good", "icon": "✓",
                "label": "Dominasi Cuaca Cerah",
                "text": f"<strong>{normal_pct:.0f}%</strong> data periode ini berstatus Normal. "
                        f"Kondisi penerbangan umumnya aman."
            })

    # ── 6. Info visibilitas ───────────────────────────────────────────────────
    if "visibilitas" in df.columns:
        vis_mean = df["visibilitas"].mean()
        insights.append({
            "level": "info", "icon": "ℹ",
            "label": "Visibilitas Rata-rata",
            "text": f"Jarak pandang rata-rata <strong>{vis_mean:.1f} km</strong>. "
                    f"{'Visibilitas baik untuk penerbangan.' if vis_mean >= 5 else 'Visibilitas rendah, perlu perhatian khusus.'}"
        })

    return insights[:6]  # max 6 insight


def generate_recommendations(
    df: pd.DataFrame,
    suhu_threshold: float = 35.0,
    hujan_threshold: float = 20.0,
    angin_threshold: float = 40.0,
) -> List[Dict]:
    """
    Generate rekomendasi operasional berdasarkan kondisi cuaca.

    Returns:
        List of dict: [{"icon", "title", "text"}, ...]
    """
    recommendations = []
    if df.empty:
        return _default_recommendations()

    has_ekstrim   = "hujan_total" in df.columns and df["hujan_total"].max() >= hujan_threshold
    has_angin     = "angin_avg"   in df.columns and df["angin_avg"].max() >= angin_threshold * 0.8
    has_suhu_tin  = "suhu_avg"    in df.columns and df["suhu_avg"].max() >= suhu_threshold

    # ── Personel ─────────────────────────────────────────────────────────────
    if has_ekstrim or has_angin:
        recommendations.append({
            "icon": "👥",
            "title": "Tambah Personel Siaga",
            "text": "Kerahkan tim ekstra 12:00–18:00 WIB saat intensitas hujan dan angin tinggi "
                    "berdasarkan pola historis data."
        })
    else:
        recommendations.append({
            "icon": "👥",
            "title": "Personel Normal",
            "text": "Tidak perlu penambahan personel. Kondisi cuaca dalam batas aman operasional harian."
        })

    # ── Penerbangan ───────────────────────────────────────────────────────────
    if has_angin or has_ekstrim:
        recommendations.append({
            "icon": "✈️",
            "title": "Notifikasi Maskapai",
            "text": "Kirim informasi kesiapsiagaan ke maskapai untuk penerbangan slot 14:00–16:00. "
                    "Potensi delay tinggi. Siapkan rencana alternatif."
        })
    else:
        recommendations.append({
            "icon": "✈️",
            "title": "Kondisi Penerbangan Aman",
            "text": "Tidak ada peringatan penerbangan khusus. Jadwal normal dapat berjalan sesuai rencana."
        })

    # ── Notifikasi ────────────────────────────────────────────────────────────
    thresholds_str = f"angin >{angin_threshold:.0f} km/h atau hujan >{hujan_threshold:.0f}mm/jam"
    recommendations.append({
        "icon": "🔔",
        "title": "Notifikasi Supervisor",
        "text": f"Aktifkan notifikasi otomatis ke supervisor bila terdeteksi {thresholds_str}. "
                f"Gunakan mekanisme laporan manual saat ini."
    })

    # ── Laporan ───────────────────────────────────────────────────────────────
    recommendations.append({
        "icon": "📋",
        "title": "Laporan Harian",
        "text": "Ringkasan cuaca harian tersedia di tab 'Laporan Per Jam'. "
                "Siapkan laporan sore pukul 17:30 WIB untuk evaluasi internal."
    })

    # ── Suhu ekstrim ──────────────────────────────────────────────────────────
    if has_suhu_tin:
        recommendations.append({
            "icon": "🌡️",
            "title": "Peringatan Suhu Tinggi",
            "text": f"Suhu melebihi {suhu_threshold}°C terdeteksi. Batasi aktivitas outdoor petugas "
                    f"antara pukul 11:00–15:00. Pastikan ketersediaan air minum."
        })

    return recommendations[:4]


def _default_recommendations() -> List[Dict]:
    return [
        {"icon": "👥", "title": "Siapkan Tim Siaga",
         "text": "Evaluasi jadwal personel berdasarkan pola cuaca historis periode 12:00–18:00."},
        {"icon": "✈️", "title": "Koordinasi Maskapai",
         "text": "Pastikan informasi cuaca terkini tersedia untuk operator penerbangan."},
        {"icon": "🔔", "title": "Sistem Notifikasi",
         "text": "Atur threshold notifikasi sesuai SOP operasional BMKG Juanda."},
        {"icon": "📋", "title": "Laporan Rutin",
         "text": "Buat ringkasan laporan cuaca harian untuk evaluasi operasional."},
    ]
