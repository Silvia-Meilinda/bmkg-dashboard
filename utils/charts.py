"""
utils/charts.py
Semua fungsi pembuatan grafik Plotly untuk BMKG Juanda Dashboard
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ── Tema warna global ────────────────────────────────────────────────────────
BG     = "#04080f"
SURF   = "#0b1420"
SURF2  = "#111d2e"
GRID   = "rgba(0,180,255,0.06)"
ACCENT = "#00b4ff"
GREEN  = "#00ffc8"
ORANGE = "#ff6b35"
RAIN   = "#4a9eff"
WARN   = "#ffb800"
MUTED  = "#6b8aaa"
TEXT   = "#e2edf8"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=BG,
    plot_bgcolor=SURF,
    font=dict(family="Space Mono, monospace", color=MUTED, size=11),
    margin=dict(t=30, b=50, l=60, r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    xaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=MUTED),
    yaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=MUTED),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor=SURF2,
        font=dict(family="Space Mono, monospace", color=TEXT, size=11),
        bordercolor=ACCENT,
    ),
)


def apply_layout(fig, **overrides):
    """Terapkan layout default ke figure."""
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 1. CHART SUHU PER JAM
# ─────────────────────────────────────────────────────────────────────────────
def make_temp_chart(df: pd.DataFrame) -> go.Figure:
    """Line chart tren suhu per jam dengan area fill."""
    fig = go.Figure()

    if df.empty or "suhu_avg" not in df.columns:
        fig.add_annotation(text="Tidak ada data suhu", x=0.5, y=0.5, showarrow=False,
                           font=dict(color=MUTED))
        return apply_layout(fig, height=300)

    x = df["jam_label"] if "jam_label" in df.columns else df["jam"].astype(str)

    # Area fill
    fig.add_trace(go.Scatter(
        x=x, y=df["suhu_avg"],
        name="Suhu Rata-rata",
        mode="lines",
        line=dict(color=ORANGE, width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(255,107,53,0.08)",
        hovertemplate="<b>%{x}</b><br>Suhu: %{y:.1f}°C<extra></extra>",
    ))

    # Min-max band
    if "suhu_min" in df.columns and "suhu_max" in df.columns:
        fig.add_trace(go.Scatter(
            x=pd.concat([x, x[::-1]]) if hasattr(x, 'iloc') else list(x) + list(x)[::-1],
            y=pd.concat([df["suhu_max"], df["suhu_min"][::-1]]) if hasattr(df["suhu_min"], 'iloc')
              else list(df["suhu_max"]) + list(df["suhu_min"])[::-1],
            fill="toself",
            fillcolor="rgba(255,107,53,0.05)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Range Min-Max",
            hoverinfo="skip",
        ))

    # Garis threshold suhu tinggi
    fig.add_hline(y=35, line_dash="dash", line_color="rgba(255,85,85,0.4)",
                  annotation_text="Batas Ekstrim 35°", annotation_font_color="#ff5555",
                  annotation_font_size=10)

    apply_layout(fig,
        height=300,
        yaxis_title="Suhu (°C)",
        xaxis_title="Jam",
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2. CHART CURAH HUJAN
# ─────────────────────────────────────────────────────────────────────────────
def make_rain_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart curah hujan per jam."""
    fig = go.Figure()

    if df.empty or "hujan_total" not in df.columns:
        fig.add_annotation(text="Tidak ada data hujan", x=0.5, y=0.5, showarrow=False,
                           font=dict(color=MUTED))
        return apply_layout(fig, height=300)

    x = df["jam_label"] if "jam_label" in df.columns else df["jam"].astype(str)
    y = df["hujan_total"]

    # Warna bar berdasarkan intensitas
    colors = []
    for v in y:
        if v >= 20:   colors.append("rgba(255,85,85,0.85)")
        elif v >= 10: colors.append("rgba(255,107,53,0.8)")
        elif v >= 5:  colors.append("rgba(74,158,255,0.85)")
        else:         colors.append("rgba(74,158,255,0.45)")

    fig.add_trace(go.Bar(
        x=x, y=y,
        name="Curah Hujan",
        marker_color=colors,
        marker_line=dict(width=0),
        hovertemplate="<b>%{x}</b><br>Hujan: %{y:.1f} mm<extra></extra>",
    ))

    # Line rata-rata
    if len(y) > 0:
        avg = y.mean()
        fig.add_hline(y=avg, line_dash="dash", line_color=f"rgba(0,180,255,0.5)",
                      annotation_text=f"Rata-rata {avg:.1f}mm",
                      annotation_font_color=ACCENT, annotation_font_size=10)

    fig.add_hline(y=20, line_dash="dot", line_color="rgba(255,85,85,0.35)",
                  annotation_text="Lebat", annotation_font_color="#ff5555", annotation_font_size=10)

    apply_layout(fig, height=300, yaxis_title="Curah Hujan (mm)", xaxis_title="Jam")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3. WIND ROSE
# ─────────────────────────────────────────────────────────────────────────────
def make_wind_rose(df_hourly: pd.DataFrame, df_raw: pd.DataFrame = None) -> go.Figure:
    """
    Wind Rose chart distribusi arah & kecepatan angin.
    Gunakan df_raw jika ada kolom arah_angin, fallback ke distribusi acak.
    """
    directions  = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    theta_names = ["U", "TL", "T", "TG", "S", "BD", "B", "BL"]

    if df_raw is not None and "arah_angin" in df_raw.columns:
        counts = df_raw["arah_angin"].value_counts()
        r_vals = [counts.get(d, 0) for d in directions]
    else:
        # Demo distribution bias ke N dan W (pola khas Surabaya)
        np.random.seed(7)
        base = np.array([35, 12, 10, 8, 15, 10, 25, 18])
        r_vals = base + np.random.randint(0, 8, 8)

    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=r_vals,
        theta=theta_names,
        name="Frekuensi",
        marker=dict(
            color=r_vals,
            colorscale=[[0, "rgba(0,255,200,0.15)"], [0.5, "rgba(0,180,255,0.6)"], [1, "rgba(0,255,200,0.9)"]],
            showscale=False,
            line=dict(color="rgba(0,255,200,0.3)", width=1),
        ),
        hovertemplate="<b>%{theta}</b><br>Frekuensi: %{r}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=SURF,
            radialaxis=dict(
                gridcolor=GRID,
                linecolor=GRID,
                tickfont=dict(color=MUTED, size=9),
                tickcolor=MUTED,
            ),
            angularaxis=dict(
                gridcolor=GRID,
                linecolor=GRID,
                tickfont=dict(color=TEXT, size=11, family="Space Mono"),
                direction="clockwise",
                rotation=90,
            ),
        ),
        paper_bgcolor=BG,
        font=dict(family="Space Mono", color=MUTED, size=11),
        showlegend=False,
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        hoverlabel=dict(bgcolor=SURF2, font=dict(family="Space Mono", color=TEXT, size=11)),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4. HEATMAP INTENSITAS CUACA
# ─────────────────────────────────────────────────────────────────────────────
def make_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap intensitas cuaca: baris = jam, kolom = hari."""
    hours = list(range(6, 22))
    days  = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]

    if not df.empty and "jam" in df.columns and "hujan_total" in df.columns:
        # Gunakan data nyata jika tersedia
        if "tanggal_date" in df.columns:
            df2 = df.copy()
            df2["day_of_week"] = pd.to_datetime(df2["tanggal_date"]).dt.dayofweek
            pivot = df2.pivot_table(
                values="hujan_total", index="jam", columns="day_of_week",
                aggfunc="mean"
            ).reindex(index=hours, columns=range(7)).fillna(0)
            z = pivot.values
        else:
            z = _demo_heatmap(hours, days)
    else:
        z = _demo_heatmap(hours, days)

    hour_labels = [f"{h:02d}:00" for h in hours]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=days,
        y=hour_labels,
        colorscale=[
            [0.0,  "rgba(0,180,255,0.08)"],
            [0.25, "rgba(0,180,255,0.35)"],
            [0.5,  "rgba(255,184,0,0.6)"],
            [0.75, "rgba(255,107,53,0.8)"],
            [1.0,  "rgba(255,50,50,0.95)"],
        ],
        hoverongaps=False,
        hovertemplate="<b>%{x} %{y}</b><br>Intensitas: %{z:.1f} mm<extra></extra>",
        colorbar=dict(
            tickfont=dict(color=MUTED, size=9, family="Space Mono"),
            title=dict(text="mm", font=dict(color=MUTED, size=10)),
            outlinecolor=GRID,
            outlinewidth=1,
            bgcolor=SURF,
        ),
    ))

    apply_layout(fig,
        height=350,
        yaxis=dict(autorange="reversed", gridcolor=GRID, tickfont=dict(size=9)),
        xaxis=dict(side="top", gridcolor=GRID),
    )
    return fig


def _demo_heatmap(hours, days):
    """Generate heatmap demo dengan pola realistis."""
    np.random.seed(12)
    z = np.zeros((len(hours), len(days)))
    for i, h in enumerate(hours):
        for j in range(len(days)):
            base = 8 if 12 <= h <= 16 else 2 if 9 <= h <= 18 else 0.5
            z[i, j] = max(0, np.random.exponential(base) * np.random.uniform(0.3, 1.5))
    return z


# ─────────────────────────────────────────────────────────────────────────────
# 5. KELEMBAPAN
# ─────────────────────────────────────────────────────────────────────────────
def make_humidity_chart(df: pd.DataFrame) -> go.Figure:
    """Gauge + line chart kelembapan."""
    fig = go.Figure()

    if df.empty or "lembap_avg" not in df.columns:
        return apply_layout(fig, height=250)

    x = df["jam_label"] if "jam_label" in df.columns else df["jam"].astype(str)

    fig.add_trace(go.Scatter(
        x=x, y=df["lembap_avg"],
        name="Kelembapan (%)",
        mode="lines+markers",
        line=dict(color=ACCENT, width=2, shape="spline"),
        marker=dict(size=4, color=ACCENT),
        fill="tozeroy",
        fillcolor="rgba(0,180,255,0.06)",
        hovertemplate="<b>%{x}</b><br>Lembap: %{y:.0f}%<extra></extra>",
    ))

    fig.add_hrect(y0=90, y1=100, fillcolor="rgba(255,184,0,0.05)",
                  line_width=0, annotation_text="Sangat Lembap",
                  annotation_font_color=WARN, annotation_font_size=9)

    apply_layout(fig, height=250, yaxis_title="Kelembapan (%)", xaxis_title="Jam",
                 yaxis_range=[40, 105])
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 6. MULTI-PARAMETER CHART
# ─────────────────────────────────────────────────────────────────────────────
def make_multi_param_chart(df: pd.DataFrame, params: list) -> go.Figure:
    """Grafik gabungan beberapa parameter dengan dual axis."""
    param_map = {
        "Suhu (°C)":           ("suhu_avg",    ORANGE, "Suhu (°C)"),
        "Curah Hujan (mm)":    ("hujan_total", RAIN,   "Hujan (mm)"),
        "Angin (km/h)":        ("angin_avg",   GREEN,  "Angin (km/h)"),
        "Kelembapan (%)":      ("lembap_avg",  ACCENT, "Lembap (%)"),
    }

    n_axis = min(len(params), 2)
    specs  = [[{"secondary_y": True}]] if n_axis == 2 else [[{"secondary_y": False}]]
    fig    = make_subplots(rows=1, cols=1, specs=specs)

    x = df["jam_label"] if "jam_label" in df.columns else df.get("jam", pd.Series(range(len(df)))).astype(str)

    for i, p in enumerate(params):
        if p not in param_map:
            continue
        col, color, label = param_map[p]
        if col not in df.columns:
            continue

        is_secondary = i >= 1
        fig.add_trace(
            go.Scatter(
                x=x, y=df[col],
                name=label,
                mode="lines+markers",
                line=dict(color=color, width=2.2, shape="spline"),
                marker=dict(size=3, color=color),
                hovertemplate=f"<b>%{{x}}</b><br>{label}: %{{y:.1f}}<extra></extra>",
            ),
            secondary_y=is_secondary
        )

    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=SURF,
        font=dict(family="Space Mono, monospace", color=MUTED, size=11),
        margin=dict(t=30, b=50, l=60, r=60),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
        hovermode="x unified",
        height=350,
        hoverlabel=dict(bgcolor=SURF2, font=dict(family="Space Mono", color=TEXT, size=11)),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, tickcolor=MUTED, title_text="Jam")
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, tickcolor=MUTED, secondary_y=False)
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, tickcolor=MUTED, secondary_y=True)
    return fig
