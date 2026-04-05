import hashlib
import uuid
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from ..extensions import db
from ..models.bathroom import Bathroom
from ..models.rating import Rating

ratings_bp = Blueprint("ratings", __name__)


def get_session_id():
    if "uid" not in session:
        session["uid"] = str(uuid.uuid4())
    raw = session["uid"]
    return hashlib.sha256(raw.encode()).hexdigest()


@ratings_bp.route("/bathroom/<int:bathroom_id>/rate", methods=["GET"])
def rate_form(bathroom_id):
    b = Bathroom.query.get_or_404(bathroom_id)
    session_id = get_session_id()
    existing = Rating.query.filter_by(bathroom_id=bathroom_id, session_id=session_id).first()
    return render_template("rate.html", bathroom=b, existing=existing)


@ratings_bp.route("/bathroom/<int:bathroom_id>/rate", methods=["POST"])
def rate_submit(bathroom_id):
    b = Bathroom.query.get_or_404(bathroom_id)
    session_id = get_session_id()

    try:
        cleanliness = int(request.form.get("cleanliness", 0))
        toilet_paper = int(request.form.get("toilet_paper", 0))
        soap = int(request.form.get("soap", 0))
    except (ValueError, TypeError):
        return redirect(url_for("ratings.rate_form", bathroom_id=bathroom_id))

    for val in (cleanliness, toilet_paper, soap):
        if not (1 <= val <= 5):
            return redirect(url_for("ratings.rate_form", bathroom_id=bathroom_id))

    comment = (request.form.get("comment") or "").strip()[:500] or None

    existing = Rating.query.filter_by(bathroom_id=bathroom_id, session_id=session_id).first()
    if existing:
        existing.cleanliness = cleanliness
        existing.toilet_paper = toilet_paper
        existing.soap = soap
        existing.overall_score = round((cleanliness + toilet_paper + soap) / 3.0, 2)
        existing.comment = comment
    else:
        rating = Rating(
            bathroom_id=bathroom_id,
            cleanliness=cleanliness,
            toilet_paper=toilet_paper,
            soap=soap,
            session_id=session_id,
            comment=comment,
        )
        db.session.add(rating)

    db.session.commit()
    return redirect(url_for("bathrooms.detail", bathroom_id=bathroom_id))


@ratings_bp.route("/api/bathrooms/<int:bathroom_id>/rate", methods=["POST"])
def api_rate(bathroom_id):
    b = Bathroom.query.get_or_404(bathroom_id)
    session_id = get_session_id()
    data = request.get_json(silent=True) or {}

    try:
        cleanliness = int(data.get("cleanliness", 0))
        toilet_paper = int(data.get("toilet_paper", 0))
        soap = int(data.get("soap", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid rating values"}), 400

    for val in (cleanliness, toilet_paper, soap):
        if not (1 <= val <= 5):
            return jsonify({"error": "Ratings must be between 1 and 5"}), 400

    comment = (data.get("comment") or "").strip()[:500] or None

    existing = Rating.query.filter_by(bathroom_id=bathroom_id, session_id=session_id).first()
    if existing:
        existing.cleanliness = cleanliness
        existing.toilet_paper = toilet_paper
        existing.soap = soap
        existing.overall_score = round((cleanliness + toilet_paper + soap) / 3.0, 2)
        existing.comment = comment
    else:
        rating = Rating(
            bathroom_id=bathroom_id,
            cleanliness=cleanliness,
            toilet_paper=toilet_paper,
            soap=soap,
            session_id=session_id,
            comment=comment,
        )
        db.session.add(rating)

    db.session.commit()
    return jsonify(b.rating_summary)
