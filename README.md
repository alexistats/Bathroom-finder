# Brantford Bathroom Finder

A community-powered Python web app that maps public washrooms in Brantford, Ontario — with **exact indoor location details** so you know where to find the bathroom *inside* the building.

## Features

- Interactive map of public bathrooms in Brantford, ON
- Exact indoor location description for each bathroom (e.g. "2nd floor near elevator, past reference desk")
- Color-coded markers by rating (green/orange/red/grey)
- "Find Bathrooms Near Me" button with distance sorting
- Rate each bathroom on **cleanliness**, **toilet paper**, and **soap** (1–5)
- Community bathroom suggestion form
- Admin review queue for community submissions

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.x + SQLAlchemy + Flask-Migrate |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Map | Folium (server-side Leaflet.js) |
| Distance | geopy (Haversine) |
| Frontend | Bootstrap 5 + vanilla JS |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and configure environment
cp .env.example .env

# 3. Initialize the database
flask db upgrade

# 4. Seed Brantford bathroom data
python seed_data/seed.py

# 5. Run the development server
flask run
```

Then open [http://localhost:5000](http://localhost:5000).

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
app/
  models/       — SQLAlchemy models (Bathroom, Rating)
  routes/       — Flask blueprints (main, bathrooms, ratings)
  services/     — Business logic (map, geo, overpass)
  templates/    — Jinja2 HTML templates
  static/       — CSS and JavaScript
seed_data/      — Manual JSON seed + seed script
tests/          — pytest test suite
migrations/     — Alembic DB migrations
```

## Adding a Bathroom

Visit `/suggest` in the app to submit a new location. Submissions are held for admin review before appearing on the map.

## Admin

Access the review queue at `/admin/submissions?password=YOUR_ADMIN_PASSWORD`.

Set `ADMIN_PASSWORD` in your `.env` file.

## Data Sources

- Manually curated entries for major Brantford locations (library, sports centre, city hall, hospital, etc.)
- OpenStreetMap Overpass API for any OSM-tagged public toilets in the Brantford bounding box
