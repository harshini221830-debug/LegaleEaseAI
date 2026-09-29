from fastapi.testclient import TestClient

from backend.main import app
from backend.config import get_settings


client = TestClient(app)


def test_generation_demo(
    monkeypatch
):

    settings = get_settings()

    monkeypatch.setattr(
        settings,
        "demo_mode",
        True
    )


    payload = {

        "document_type":
            "Freelance Work Contract",

        "parties":
            "Jane Doe (Freelancer), "
            "ABC Corp (Client)",

        "terms":
            "Payment within 30 days; "
            "Confidentiality must be maintained",

        "effective_date":
            "2026-09-28"
    }


    response = client.post(

        "/generate",

        json=payload
    )


    assert response.status_code == 200


    data = response.json()


    assert data["success"] is True


    assert (
        "Freelance Work Contract"
        in data["text"]
    )


    assert data["demo_mode"] is True