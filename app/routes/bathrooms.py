from flask import Blueprint, jsonify, render_template, request, abort
from ..models.bathroom import Bathroom
from ..services.geo_service import sort_by_distance, filter_by_radius, format_distance

bathrooms_bp = Blueprint("bathrooms", __name__)


@bathrooms_bp.route("/bathroom/<int:bathroom_id>")
def detail(bathroom_id):
    b = Bathroom.query.get_or_404(bathroom_id)
    summary = b.rating_summary
    recent_ratings = b.ratings.order_by(
        __import__("app.models.rating", fromlist=["Rating"]).Rating.created_at.desc()
    ).limit(10).all()
    return render_template(
        "bathroom_detail.html",
        bathroom=b,
        summary=summary,
        recent_ratings=recent_ratings,
    )


@bathrooms_bp.route("/api/bathrooms")
def api_list():
    query = Bathroom.query.filter_by(is_verified=True)

    accessible = request.args.get("accessible")
    if accessible == "true":
        query = query.filter_by(accessibility=True)

    gender = request.args.get("gender")
    if gender:
        query = query.filter_by(gender_type=gender)

    bathrooms = query.all()

    # Geolocation-based sort/filter
    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))
        radius = float(request.args.get("radius", 5.0))
        pairs = filter_by_radius(bathrooms, lat, lon, radius)
        result = []
        for b, dist in pairs:
            d = b.to_dict(include_ratings=True)
            d["distance_km"] = dist
            d["distance_label"] = format_distance(dist)
            result.append(d)
        return jsonify(result)
    except (ValueError, TypeError):
        pass

    # No geolocation — return all sorted by name
    result = [b.to_dict(include_ratings=True) for b in bathrooms]
    return jsonify(result)


@bathrooms_bp.route("/api/bathrooms/<int:bathroom_id>/ratings")
def api_ratings(bathroom_id):
    from ..models.rating import Rating
    b = Bathroom.query.get_or_404(bathroom_id)
    ratings = b.ratings.order_by(Rating.created_at.desc()).limit(20).all()
    return jsonify([r.to_dict() for r in ratings])
