import json


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Brantford" in resp.data or b"bathroom" in resp.data.lower()


def test_api_bathrooms_returns_json(client):
    resp = client.get("/api/bathrooms")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_bathroom_detail_404(client):
    resp = client.get("/bathroom/99999")
    assert resp.status_code == 404


def test_bathroom_detail_ok(client, sample_bathroom):
    resp = client.get(f"/bathroom/{sample_bathroom.id}")
    assert resp.status_code == 200
    assert sample_bathroom.name.encode() in resp.data


def test_rate_form_get(client, sample_bathroom):
    resp = client.get(f"/bathroom/{sample_bathroom.id}/rate")
    assert resp.status_code == 200
    assert b"Rate" in resp.data


def test_rate_submit_valid(client, sample_bathroom):
    resp = client.post(
        f"/bathroom/{sample_bathroom.id}/rate",
        data={"cleanliness": "4", "toilet_paper": "3", "soap": "5", "comment": "Clean!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_rate_submit_invalid_values(client, sample_bathroom):
    resp = client.post(
        f"/bathroom/{sample_bathroom.id}/rate",
        data={"cleanliness": "6", "toilet_paper": "0", "soap": "3"},
        follow_redirects=True,
    )
    # Should redirect back to form (not crash)
    assert resp.status_code == 200


def test_api_bathrooms_nearby_filter(client, sample_bathroom):
    # sample_bathroom is at 43.14, -80.27
    resp = client.get("/api/bathrooms?lat=43.14&lon=-80.27&radius=1.0")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    ids = [b["id"] for b in data]
    assert sample_bathroom.id in ids


def test_suggest_get(client):
    resp = client.get("/suggest")
    assert resp.status_code == 200
    assert b"Suggest" in resp.data


def test_admin_requires_password(client):
    resp = client.get("/admin/submissions")
    assert resp.status_code == 403


def test_admin_with_correct_password(client, app):
    password = app.config["ADMIN_PASSWORD"]
    resp = client.get(f"/admin/submissions?password={password}")
    assert resp.status_code == 200
