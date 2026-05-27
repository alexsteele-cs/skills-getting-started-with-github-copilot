from urllib.parse import quote

import src.app as app_module


def signup_path(activity_name: str) -> str:
    encoded_activity_name = quote(activity_name, safe="")
    return f"/activities/{encoded_activity_name}/signup"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_success(client):
    email = "new.student@mergington.edu"

    response = client.post(signup_path("Chess Club"), params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_registration(client):
    email = "duplicate.student@mergington.edu"
    client.post(signup_path("Chess Club"), params={"email": email})

    response = client.post(signup_path("Chess Club"), params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_activity_rejects_when_activity_is_full(client):
    activity_name = "Tennis Club"
    max_participants = app_module.activities[activity_name]["max_participants"]
    app_module.activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(max_participants)
    ]

    response = client.post(
        signup_path(activity_name),
        params={"email": "overflow.student@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_for_missing_activity_returns_404(client):
    response = client.post(
        signup_path("Nonexistent Club"),
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_success(client):
    activity_name = "Programming Class"
    email = "temp.student@mergington.edu"
    app_module.activities[activity_name]["participants"].append(email)

    response = client.delete(signup_path(activity_name), params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_non_enrolled_participant_returns_404(client):
    response = client.delete(
        signup_path("Gym Class"),
        params={"email": "not.enrolled@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_from_missing_activity_returns_404(client):
    response = client.delete(
        signup_path("Imaginary Club"),
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
