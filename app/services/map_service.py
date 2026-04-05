import folium
from folium.plugins import LocateControl

BRANTFORD_CENTER = [43.1394, -80.2644]

GENDER_LABELS = {
    "gender_neutral": "Gender Neutral",
    "male_female": "Male / Female",
    "all_gender": "All Gender",
}


def _marker_color(avg_overall, count):
    if count == 0:
        return "gray"
    if avg_overall >= 4.0:
        return "green"
    if avg_overall >= 2.5:
        return "orange"
    return "red"


def _star_html(score, max_stars=5):
    filled = int(round(score))
    stars = "★" * filled + "☆" * (max_stars - filled)
    return f'<span style="color:#f5a623;font-size:14px">{stars}</span>'


def _popup_html(bathroom, summary):
    avg_c = summary["avg_cleanliness"]
    avg_tp = summary["avg_toilet_paper"]
    avg_s = summary["avg_soap"]
    avg_o = summary["avg_overall"]
    count = summary["count"]
    indoor = bathroom.indoor_location or "<em>Indoor location not yet added — help us by suggesting details!</em>"
    floor_badge = bathroom.floor or "Ground Floor"
    gender = GENDER_LABELS.get(bathroom.gender_type, bathroom.gender_type)
    access_icon = "♿ " if bathroom.accessibility else ""
    hours = bathroom.hours_open or "Hours not listed"
    rating_section = (
        f"""
        <div style="margin:6px 0">
          <small>
            🧹 Cleanliness: {_star_html(avg_c)} ({avg_c}/5)<br>
            🧻 Toilet Paper: {_star_html(avg_tp)} ({avg_tp}/5)<br>
            🧼 Soap: {_star_html(avg_s)} ({avg_s}/5)
          </small>
          <div style="font-size:11px;color:#888;margin-top:3px">{count} rating{"s" if count != 1 else ""}</div>
        </div>
        """
        if count > 0
        else '<div style="color:#888;font-size:12px;margin:6px 0">No ratings yet — be the first!</div>'
    )

    return f"""
<div style="min-width:220px;max-width:280px;font-family:sans-serif;font-size:13px">
  <strong style="font-size:14px">{bathroom.name}</strong><br>
  <small style="color:#666">{bathroom.address}</small>
  <hr style="margin:6px 0;border-color:#eee">
  <span style="background:#f0ad4e;color:#fff;padding:2px 7px;border-radius:3px;font-size:11px">{floor_badge}</span>
  &nbsp;<span style="font-size:11px;color:#555">{access_icon}{gender}</span>
  <p style="margin:8px 0 4px 0;font-size:12px">
    <strong>📍 Where inside:</strong><br>
    {indoor}
  </p>
  <p style="margin:4px 0;font-size:11px;color:#666">🕐 {hours}</p>
  <hr style="margin:6px 0;border-color:#eee">
  {rating_section}
  <div style="margin-top:6px">
    <a href="/bathroom/{bathroom.id}" style="background:#0d6efd;color:#fff;padding:4px 10px;border-radius:4px;text-decoration:none;font-size:12px">
      Full Details &amp; Rate →
    </a>
  </div>
</div>
"""


def build_map(bathrooms_with_summaries, center=None):
    """
    Build and return a Folium map HTML string.

    bathrooms_with_summaries: list of (Bathroom, summary_dict) tuples
    center: [lat, lon] or None (defaults to Brantford centre)
    """
    m = folium.Map(
        location=center or BRANTFORD_CENTER,
        zoom_start=14,
        tiles="OpenStreetMap",
    )

    LocateControl(auto_start=False, keepCurrentZoomLevel=True).add_to(m)

    for bathroom, summary in bathrooms_with_summaries:
        color = _marker_color(summary["avg_overall"], summary["count"])
        popup_html = _popup_html(bathroom, summary)

        folium.Marker(
            location=[bathroom.latitude, bathroom.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=bathroom.name,
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)

    return m._repr_html_()


def build_map_for_bathrooms(bathrooms):
    """Convenience wrapper: build the map from a list of Bathroom ORM objects."""
    pairs = [(b, b.rating_summary) for b in bathrooms]
    return build_map(pairs)
