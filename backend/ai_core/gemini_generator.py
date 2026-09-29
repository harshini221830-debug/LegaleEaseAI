from __future__ import annotations

import time

from google import genai
from google.genai import types

from backend.config import Settings


class GeminiDocumentGenerator:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None

        if not settings.demo_mode:

            if not settings.gemini_api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is missing. "
                    "Add it to .env or set DEMO_MODE=true."
                )

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    @staticmethod
    def demo_document(request) -> str:

        terms = [
            item.strip()
            for item in request.terms
            .replace("\n", ";")
            .split(";")
            if item.strip()
        ]

        document = []

        document.append(request.document_type.upper())
        document.append("")

        document.append(
            f"Effective Date: {request.effective_date}"
        )

        document.append(
            f"Parties: {request.parties}"
        )

        document.append("")

        document.append("1. PURPOSE")

        document.append(
            f"This draft describes the principal terms "
            f"for the {request.document_type}."
        )

        document.append("")

        document.append("2. TERMS AND CONDITIONS")

        for index, term in enumerate(terms, start=1):
            document.append(f"{index}. {term}")

        if request.jurisdiction:
            document.append("")
            document.append(
                "3. GOVERNING LAW / JURISDICTION"
            )
            document.append(request.jurisdiction)

        document.append("")
        document.append("4. GENERAL")

        document.append(
            "This is a demonstration draft generated "
            "locally. It must be reviewed and adapted "
            "to the applicable law and facts before use."
        )

        document.append("")
        document.append("DISCLAIMER")

        document.append(
            "LegalEase is an informational drafting tool "
            "and does not provide legal advice."
        )

        return "\n".join(document)

    def build_prompt(self, request) -> str:

        return f"""
You are a careful legal-document drafting assistant.

Create a structured FIRST DRAFT of the requested
legal document using only the information supplied
by the user.

Do not invent:

- names
- amounts
- dates
- addresses
- obligations
- laws
- statutes
- factual claims

If important information is missing, use:

[TO BE COMPLETED]

PROJECT:
LegalEase

DOCUMENT TYPE:
{request.document_type}

PARTIES:
{request.parties}

EFFECTIVE DATE:
{request.effective_date}

JURISDICTION:
{request.jurisdiction or "[TO BE COMPLETED]"}

TERMS AND CONDITIONS:
{request.terms}

ADDITIONAL INSTRUCTIONS:
{request.additional_instructions or "None"}

OUTPUT REQUIREMENTS:

1. Use clear numbered headings.
2. Include the document title.
3. Include the effective date.
4. Include the parties.
5. Convert the supplied terms into appropriate clauses
   without changing their meaning.
6. Include signature blocks where appropriate.
7. Use [TO BE COMPLETED] for important missing information.
8. Do not claim that the document is legally valid.
9. Do not claim that the document is legally sound.
10. Do not provide fabricated laws or legal citations.

End the document with:

LegalEase notice:
This is an AI-generated draft for informational
purposes and should be reviewed by a qualified
legal professional before use.
"""

    def generate_document(self, request) -> str:

        if self.settings.demo_mode:
            return self.demo_document(request)

        if self.client is None:
            raise RuntimeError(
                "Gemini client is not initialized."
            )

        prompt = self.build_prompt(request)

        max_attempts = 3
        last_error = None

        for attempt in range(max_attempts):

            try:

                response = self.client.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=8000
                    )
                )

                text = (response.text or "").strip()

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return text

            except Exception as exc:

                last_error = exc
                error_text = str(exc).lower()

                temporary_error = (
                    "503" in error_text
                    or "unavailable" in error_text
                    or "high demand" in error_text
                    or "temporarily" in error_text
                )

                if not temporary_error:
                    raise

                if attempt < max_attempts - 1:

                    wait_seconds = 2 ** attempt

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)

        raise RuntimeError(
            "Gemini is temporarily unavailable after "
            f"{max_attempts} attempts. "
            f"Please try again shortly. "
            f"Original error: {last_error}"
        )