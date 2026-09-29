from typing import Literal

from pydantic import BaseModel, Field, field_validator


DocumentFormat = Literal["txt", "docx", "pdf"]


class DocumentRequest(BaseModel):

    document_type: str = Field(
        min_length=2,
        max_length=120
    )

    parties: str = Field(
        min_length=2,
        max_length=4000
    )

    terms: str = Field(
        min_length=2,
        max_length=12000
    )

    effective_date: str = Field(
        min_length=2,
        max_length=100
    )

    jurisdiction: str = Field(
        default="",
        max_length=200
    )

    additional_instructions: str = Field(
        default="",
        max_length=4000
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "effective_date"
    )
    @classmethod
    def validate_required_fields(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class GenerateResponse(BaseModel):

    success: bool

    text: str

    model: str

    demo_mode: bool

    warning: str | None = None


class ExportRequest(DocumentRequest):

    text: str = Field(
        min_length=10,
        max_length=100000
    )

    brand_name: str = Field(
        default="LegalEase",
        max_length=120
    )

    logo_base64: str | None = None