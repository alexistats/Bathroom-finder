from geopy.distance import geodesic


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Return distance in kilometres between two lat/lon points."""
    return geodesic((lat1, lon1), (lat2, lon2)).km


def sort_by_distance(bathrooms, user_lat, user_lon):
    """Return list of (bathroom, distance_km) tuples sorted nearest-first."""
    results = []
    for b in bathrooms:
        dist = haversine_distance_km(user_lat, user_lon, b.latitude, b.longitude)
        results.append((b, round(dist, 3)))
    results.sort(key=lambda x: x[1])
    return results


def filter_by_radius(bathrooms, user_lat, user_lon, radius_km=1.0):
    """Return only bathrooms within radius_km of the user."""
    return [
        (b, dist)
        for b, dist in sort_by_distance(bathrooms, user_lat, user_lon)
        if dist <= radius_km
    ]


def format_distance(km):
    """Human-readable distance string."""
    if km < 1.0:
        return f"{int(km * 1000)} m"
    return f"{km:.1f} km"
