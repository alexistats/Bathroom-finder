from app.services.geo_service import (
    haversine_distance_km,
    sort_by_distance,
    filter_by_radius,
    format_distance,
)


class FakeBathroom:
    def __init__(self, id, lat, lon):
        self.id = id
        self.latitude = lat
        self.longitude = lon


def test_haversine_same_point():
    assert haversine_distance_km(43.14, -80.27, 43.14, -80.27) == 0.0


def test_haversine_known_distance():
    # Roughly 1 km north
    dist = haversine_distance_km(43.14, -80.27, 43.15, -80.27)
    assert 1.0 < dist < 1.2


def test_sort_by_distance_orders_correctly():
    b1 = FakeBathroom(1, 43.15, -80.27)  # farther
    b2 = FakeBathroom(2, 43.141, -80.27)  # closer
    results = sort_by_distance([b1, b2], 43.14, -80.27)
    assert results[0][0].id == 2
    assert results[1][0].id == 1
    # Distances are ascending
    assert results[0][1] <= results[1][1]


def test_filter_by_radius_excludes_distant():
    b_near = FakeBathroom(1, 43.141, -80.27)   # ~0.1 km
    b_far = FakeBathroom(2, 43.20, -80.27)     # ~6+ km
    results = filter_by_radius([b_near, b_far], 43.14, -80.27, radius_km=1.0)
    ids = [b.id for b, _ in results]
    assert 1 in ids
    assert 2 not in ids


def test_format_distance_metres():
    assert format_distance(0.3) == "300 m"


def test_format_distance_km():
    assert format_distance(1.5) == "1.5 km"


def test_format_distance_boundary():
    assert format_distance(0.999) == "999 m"
    assert format_distance(1.0) == "1.0 km"
