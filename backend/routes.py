from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from backend.config import get_settings

from backend.schemas import (
    DocumentRequest,
    ExportRequest,
    GenerateResponse
)

from backend.services.document_service import (
    format_docx,
    format_pdf,
    format_txt
)


router = APIRouter()

settings = get_settings()


@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": settings.app_name,
        "demo_mode": settings.demo_mode,
        "model": settings.gemini_model
    }


@router.post(
    "/generate",
    response_model=GenerateResponse
)
def generate(
    request: DocumentRequest
):

    try:

        generator = (
            GeminiDocumentGenerator(
                settings
            )
        )

        text = (
            generator.generate_document(
                request
            )
        )

        if settings.demo_mode:

            warning = (
                "Demo mode is active. "
                "The document was generated "
                "locally without Gemini."
            )

        else:

            warning = (
                "AI-generated draft. "
                "Review it for your jurisdiction "
                "and facts before use."
            )

        return GenerateResponse(

            success=True,

            text=text,

            model=settings.gemini_model,

            demo_mode=settings.demo_mode,

            warning=warning
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc


@router.post("/export/txt")
def export_txt(
    request: ExportRequest
):

    content = format_txt(
        request.text
    )

    return Response(

        content=content,

        media_type="text/plain; charset=utf-8",

        headers={
            "Content-Disposition":
                'attachment; filename="legalease_document.txt"'
        }
    )


@router.post("/export/docx")
def export_docx(
    request: ExportRequest
):

    content = format_docx(

        request.text,

        request.document_type,

        request.brand_name,

        request.logo_base64
    )

    return Response(

        content=content,

        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),

        headers={
            "Content-Disposition":
                'attachment; filename="legalease_document.docx"'
        }
    )


@router.post("/export/pdf")
def export_pdf(
    request: ExportRequest
):

    try:

        content = format_pdf(

            request.text,

            request.document_type,

            request.brand_name,

            request.logo_base64
        )

        return Response(

            content=content,

            media_type="application/pdf",

            headers={
                "Content-Disposition":
                    'attachment; filename="legalease_document.pdf"'
            }
        )

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=f"PDF generation failed: {exc}"
        ) from exc