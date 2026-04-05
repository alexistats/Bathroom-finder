from datetime import datetime, timezone
from ..extensions import db


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    bathroom_id = db.Column(db.Integer, db.ForeignKey("bathrooms.id"), nullable=False)
    cleanliness = db.Column(db.Integer, nullable=False)
    toilet_paper = db.Column(db.Integer, nullable=False)
    soap = db.Column(db.Integer, nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, bathroom_id, cleanliness, toilet_paper, soap, session_id, comment=None):
        self.bathroom_id = bathroom_id
        self.cleanliness = cleanliness
        self.toilet_paper = toilet_paper
        self.soap = soap
        self.session_id = session_id
        self.comment = comment
        self.overall_score = round((cleanliness + toilet_paper + soap) / 3.0, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "bathroom_id": self.bathroom_id,
            "cleanliness": self.cleanliness,
            "toilet_paper": self.toilet_paper,
            "soap": self.soap,
            "overall_score": self.overall_score,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Rating bathroom={self.bathroom_id} overall={self.overall_score}>"
