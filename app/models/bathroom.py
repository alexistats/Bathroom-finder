from datetime import datetime, timezone
from sqlalchemy import func
from ..extensions import db


class Bathroom(db.Model):
    __tablename__ = "bathrooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    indoor_location = db.Column(db.String(300), nullable=True)
    floor = db.Column(db.String(50), nullable=True)
    accessibility = db.Column(db.Boolean, default=False)
    gender_type = db.Column(db.String(20), default="male_female")
    hours_open = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=True)
    osm_id = db.Column(db.String(50), nullable=True, unique=True)
    source = db.Column(db.String(50), default="manual")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    ratings = db.relationship("Rating", backref="bathroom", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def rating_summary(self):
        from ..models.rating import Rating

        result = db.session.query(
            func.avg(Rating.cleanliness).label("avg_cleanliness"),
            func.avg(Rating.toilet_paper).label("avg_toilet_paper"),
            func.avg(Rating.soap).label("avg_soap"),
            func.avg(Rating.overall_score).label("avg_overall"),
            func.count(Rating.id).label("count"),
        ).filter(Rating.bathroom_id == self.id).first()

        return {
            "avg_cleanliness": round(result.avg_cleanliness or 0, 1),
            "avg_toilet_paper": round(result.avg_toilet_paper or 0, 1),
            "avg_soap": round(result.avg_soap or 0, 1),
            "avg_overall": round(result.avg_overall or 0, 1),
            "count": result.count or 0,
        }

    def to_dict(self, include_ratings=False):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "indoor_location": self.indoor_location,
            "floor": self.floor,
            "accessibility": self.accessibility,
            "gender_type": self.gender_type,
            "hours_open": self.hours_open,
            "is_verified": self.is_verified,
            "source": self.source,
        }
        if include_ratings:
            data["ratings"] = self.rating_summary
        return data

    def __repr__(self):
        return f"<Bathroom {self.name}>"
