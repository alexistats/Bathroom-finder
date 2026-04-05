from app.models.bathroom import Bathroom
from app.models.rating import Rating


def test_bathroom_creation(db):
    b = Bathroom(
        name="Library Test",
        address="123 Main St",
        latitude=43.1,
        longitude=-80.2,
        indoor_location="2nd floor",
        floor="2nd Floor",
        accessibility=True,
        gender_type="male_female",
        is_verified=True,
        source="manual",
    )
    db.session.add(b)
    db.session.commit()
    assert b.id is not None
    assert b.name == "Library Test"


def test_rating_overall_score_computed(db, sample_bathroom):
    r = Rating(
        bathroom_id=sample_bathroom.id,
        cleanliness=4,
        toilet_paper=3,
        soap=5,
        session_id="abc123",
    )
    db.session.add(r)
    db.session.commit()
    expected = round((4 + 3 + 5) / 3.0, 2)
    assert r.overall_score == expected


def test_rating_summary_empty(db, sample_bathroom):
    summary = sample_bathroom.rating_summary
    assert summary["count"] == 0
    assert summary["avg_overall"] == 0


def test_rating_summary_with_ratings(db, sample_bathroom):
    for cleanliness, tp, soap in [(5, 5, 5), (3, 3, 3)]:
        r = Rating(
            bathroom_id=sample_bathroom.id,
            cleanliness=cleanliness,
            toilet_paper=tp,
            soap=soap,
            session_id=f"sess-{cleanliness}",
        )
        db.session.add(r)
    db.session.commit()

    summary = sample_bathroom.rating_summary
    assert summary["count"] == 2
    assert summary["avg_cleanliness"] == 4.0
    assert summary["avg_overall"] == 4.0


def test_bathroom_to_dict(sample_bathroom):
    d = sample_bathroom.to_dict()
    assert d["name"] == "Test Toilet"
    assert d["accessibility"] is True
    assert "ratings" not in d

    d_with_ratings = sample_bathroom.to_dict(include_ratings=True)
    assert "ratings" in d_with_ratings
