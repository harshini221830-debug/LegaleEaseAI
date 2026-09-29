from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


PAYLOAD = {

    "document_type":
        "General Agreement",

    "parties":
        "Alice (Party A), Bob (Party B)",

    "terms":
        "Party A will deliver the work; "
        "Party B will make payment",

    "effective_date":
        "2026-09-28",

    "text":
        """
GENERAL AGREEMENT

Effective Date: 2026-09-28

1. TERMS

Party A will deliver the work.

Party B will make payment.
""",

    "brand_name":
        "LegalEase"
}


def test_txt_export():

    response = client.post(

        "/export/txt",

        json=PAYLOAD
    )


    assert response.status_code == 200


    assert (
        response
        .headers["content-type"]
        .startswith("text/plain")
    )


    assert (
        b"GENERAL AGREEMENT"
        in response.content
    )


def test_docx_export():

    response = client.post(

        "/export/docx",

        json=PAYLOAD
    )


    assert response.status_code == 200


    # DOCX files are ZIP containers

    assert (
        response.content[:2]
        == b"PK"
    )


def test_pdf_export():

    response = client.post(

        "/export/pdf",

        json=PAYLOAD
    )


    assert response.status_code == 200


    assert (
        response.content.startswith(
            b"%PDF"
        )
    )