import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
BRANTFORD_BBOX = (43.09, -80.34, 43.20, -80.18)  # south, west, north, east


def fetch_brantford_toilets():
    """Fetch toilet nodes/ways from OpenStreetMap Overpass API for Brantford, ON."""
    south, west, north, east = BRANTFORD_BBOX
    query = f"""
[out:json][timeout:30];
(
  node["amenity"="toilets"]({south},{west},{north},{east});
  way["amenity"="toilets"]({south},{west},{north},{east});
);
out center;
"""
    resp = requests.get(OVERPASS_URL, params={"data": query}, timeout=30)
    resp.raise_for_status()
    return resp.json().get("elements", [])
