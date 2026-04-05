"""
Seed script: imports manual Brantford bathroom data + pulls from OpenStreetMap Overpass API.
Run from the project root: python seed_data/seed.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from app import create_app
from app.extensions import db
from app.models.bathroom import Bathroom

BRANTFORD_BBOX = (43.09, -80.34, 43.20, -80.18)  # south, west, north, east
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
SEED_FILE = os.path.join(os.path.dirname(__file__), "brantford_bathrooms.json")


def load_manual_data():
    with open(SEED_FILE, "r") as f:
        return json.load(f)


def fetch_osm_bathrooms():
    south, west, north, east = BRANTFORD_BBOX
    query = f"""
[out:json][timeout:30];
(
  node["amenity"="toilets"]({south},{west},{north},{east});
  way["amenity"="toilets"]({south},{west},{north},{east});
);
out center;
"""
    print("Fetching bathrooms from OpenStreetMap Overpass API...")
    try:
        resp = requests.get(OVERPASS_URL, params={"data": query}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("elements", [])
    except requests.RequestException as e:
        print(f"  Warning: Overpass API request failed: {e}")
        return []


def osm_element_to_bathroom(element):
    tags = element.get("tags", {})
    name = tags.get("name") or tags.get("operator") or "Public Toilet"

    if element["type"] == "node":
        lat = element["lat"]
        lon = element["lon"]
    else:
        center = element.get("center", {})
        lat = center.get("lat")
        lon = center.get("lon")

    if lat is None or lon is None:
        return None

    accessibility = tags.get("wheelchair") in ("yes", "designated")
    gender_type = "gender_neutral"
    if tags.get("male") == "yes" and tags.get("female") == "yes":
        gender_type = "male_female"
    elif tags.get("unisex") == "yes":
        gender_type = "gender_neutral"

    hours = tags.get("opening_hours")

    return Bathroom(
        name=name,
        address=f"Brantford, ON (OSM {element['id']})",
        latitude=lat,
        longitude=lon,
        indoor_location=None,
        floor="Ground",
        accessibility=accessibility,
        gender_type=gender_type,
        hours_open=hours,
        is_verified=False,
        osm_id=str(element["id"]),
        source="osm",
    )


def seed_manual(app):
    entries = load_manual_data()
    added = 0
    with app.app_context():
        for entry in entries:
            existing = Bathroom.query.filter_by(name=entry["name"], address=entry["address"]).first()
            if existing:
                print(f"  Skip (exists): {entry['name']}")
                continue
            b = Bathroom(
                name=entry["name"],
                address=entry["address"],
                latitude=entry["latitude"],
                longitude=entry["longitude"],
                indoor_location=entry.get("indoor_location"),
                floor=entry.get("floor"),
                accessibility=entry.get("accessibility", False),
                gender_type=entry.get("gender_type", "male_female"),
                hours_open=entry.get("hours_open"),
                is_verified=True,
                osm_id=None,
                source=entry.get("source", "manual"),
            )
            db.session.add(b)
            added += 1
            print(f"  Added: {entry['name']}")
        db.session.commit()
    return added


def seed_osm(app):
    elements = fetch_osm_bathrooms()
    added = 0
    with app.app_context():
        for element in elements:
            osm_id = str(element["id"])
            existing = Bathroom.query.filter_by(osm_id=osm_id).first()
            if existing:
                print(f"  Skip OSM (exists): {osm_id}")
                continue
            bathroom = osm_element_to_bathroom(element)
            if bathroom is None:
                continue
            db.session.add(bathroom)
            added += 1
            print(f"  Added OSM: {bathroom.name} ({osm_id})")
        db.session.commit()
    return added


def main():
    app = create_app()
    with app.app_context():
        db.create_all()

    print("\n=== Seeding manual Brantford bathroom data ===")
    manual_count = seed_manual(app)
    print(f"Manual entries added: {manual_count}")

    print("\n=== Fetching OpenStreetMap data ===")
    osm_count = seed_osm(app)
    print(f"OSM entries added: {osm_count}")

    with app.app_context():
        total = Bathroom.query.count()
    print(f"\nTotal bathrooms in database: {total}")
    print("Seeding complete.")


if __name__ == "__main__":
    main()
