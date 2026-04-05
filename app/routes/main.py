from flask import Blueprint, render_template
from ..models.bathroom import Bathroom
from ..services.map_service import build_map_for_bathrooms

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    bathrooms = Bathroom.query.filter_by(is_verified=True).all()
    map_html = build_map_for_bathrooms(bathrooms)
    return render_template("index.html", map_html=map_html, count=len(bathrooms))


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/suggest", methods=["GET"])
def suggest_get():
    return render_template("suggest.html")


@main_bp.route("/suggest", methods=["POST"])
def suggest_post():
    from flask import request, flash, redirect, url_for
    from ..extensions import db
    from ..models.bathroom import Bathroom

    name = request.form.get("name", "").strip()
    address = request.form.get("address", "").strip()
    indoor_location = request.form.get("indoor_location", "").strip()
    floor = request.form.get("floor", "").strip()
    hours_open = request.form.get("hours_open", "").strip()
    gender_type = request.form.get("gender_type", "male_female")
    accessibility = request.form.get("accessibility") == "on"

    try:
        lat = float(request.form.get("latitude", ""))
        lon = float(request.form.get("longitude", ""))
    except ValueError:
        flash("Invalid coordinates. Please enter valid latitude and longitude.", "danger")
        return render_template("suggest.html"), 400

    if not name or not address:
        flash("Name and address are required.", "danger")
        return render_template("suggest.html"), 400

    b = Bathroom(
        name=name,
        address=address,
        latitude=lat,
        longitude=lon,
        indoor_location=indoor_location or None,
        floor=floor or None,
        accessibility=accessibility,
        gender_type=gender_type,
        hours_open=hours_open or None,
        is_verified=False,
        source="community",
    )
    db.session.add(b)
    db.session.commit()
    flash("Thank you! Your bathroom suggestion has been submitted for review.", "success")
    return redirect(url_for("main.index"))


@main_bp.route("/admin/submissions")
def admin_submissions():
    from flask import request, current_app, abort
    password = request.args.get("password", "")
    if password != current_app.config.get("ADMIN_PASSWORD"):
        abort(403)
    unverified = Bathroom.query.filter_by(is_verified=False).all()
    return render_template("admin/submissions.html", bathrooms=unverified)


@main_bp.route("/admin/submissions/<int:bathroom_id>/verify", methods=["POST"])
def admin_verify(bathroom_id):
    from flask import request, current_app, abort, redirect, url_for
    from ..extensions import db

    password = request.form.get("password", "")
    if password != current_app.config.get("ADMIN_PASSWORD"):
        abort(403)
    b = Bathroom.query.get_or_404(bathroom_id)
    b.is_verified = True
    db.session.commit()
    return redirect(url_for("main.admin_submissions", password=password))


@main_bp.route("/admin/submissions/<int:bathroom_id>/delete", methods=["POST"])
def admin_delete(bathroom_id):
    from flask import request, current_app, abort, redirect, url_for
    from ..extensions import db

    password = request.form.get("password", "")
    if password != current_app.config.get("ADMIN_PASSWORD"):
        abort(403)
    b = Bathroom.query.get_or_404(bathroom_id)
    db.session.delete(b)
    db.session.commit()
    return redirect(url_for("main.admin_submissions", password=password))
