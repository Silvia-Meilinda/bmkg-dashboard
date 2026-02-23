"""
utils/helpers.py
Fungsi-fungsi pembantu umum
"""

from datetime import datetime
import pytz


def format_datetime_wib(dt: datetime = None) -> str:
    """Format datetime ke string WIB."""
    wib = pytz.timezone("Asia/Jakarta")
    if dt is None:
        dt = datetime.now(wib)
    elif dt.tzinfo is None:
        dt = wib.localize(dt)
    else:
        dt = dt.astimezone(wib)
    return dt.strftime("%A, %d %B %Y  %H:%M:%S WIB")


def get_status_badge(status: str) -> str:
    """Return HTML badge untuk status cuaca."""
    badges = {
        "Normal":  '<span class="badge badge-normal">✓ Normal</span>',
        "Hujan":   '<span class="badge badge-hujan">🌧 Hujan</span>',
        "Ekstrim": '<span class="badge badge-ekstrim">⚡ Ekstrim</span>',
        "Kabut":   '<span class="badge badge-kabut">🌫 Kabut</span>',
    }
    return badges.get(status, f'<span class="badge">{status}</span>')


def km_to_knots(km: float) -> float:
    return round(km / 1.852, 1)


def celsius_to_fahrenheit(c: float) -> float:
    return round(c * 9 / 5 + 32, 1)
