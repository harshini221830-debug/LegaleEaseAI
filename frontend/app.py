import base64
import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8001"
).rstrip("/")


st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide"
)


st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 28px;
    }

    .preview {
        background: #171717;
        color: #f2f2f2;
        padding: 24px;
        border-radius: 14px;
        min-height: 450px;
        white-space: pre-wrap;
        overflow: auto;
        font-family: Georgia, serif;
        line-height: 1.55;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="main-title">'
    '⚖️ LegalEase'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="subtitle">'
    'AI-powered legal document drafting and export'
    '</div>',
    unsafe_allow_html=True
)


with st.sidebar:

    st.header("Branding")

    brand_name = st.text_input(
        "Brand / Company Name",
        value="LegalEase"
    )

    logo = st.file_uploader(
        "Optional Logo",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    st.divider()

    st.caption(
        "LegalEase creates drafts for "
        "informational use. Important "
        "documents should be reviewed "
        "by a qualified legal professional."
    )


left_column, right_column = st.columns(2)


with left_column:

    document_type = st.selectbox(

        "Document Type",

        [
            "Employment Contract",

            "Non-Disclosure Agreement",

            "Lease Agreement",

            "Service Agreement",

            "Freelance Work Contract",

            "Employment Offer Letter",

            "General Agreement"
        ]
    )


    parties = st.text_area(

        "Parties Involved",

        placeholder=(
            "Jane Doe (Employee), "
            "ABC Technologies (Employer)"
        ),

        height=100
    )


    effective_date = st.date_input(

        "Effective Date",

        value=date.today()
    )


with right_column:

    jurisdiction = st.text_input(

        "Jurisdiction (Optional)",

        placeholder=(
            "Example: Tamil Nadu, India"
        )
    )


    terms = st.text_area(

        "Terms & Conditions",

        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),

        height=160,

        help=(
            "Separate individual terms "
            "using semicolons."
        )
    )


    additional_instructions = st.text_area(

        "Additional Instructions (Optional)",

        placeholder=(
            "Add any non-sensitive "
            "drafting preferences."
        ),

        height=90
    )


if "document_text" not in st.session_state:

    st.session_state.document_text = ""


if "metadata" not in st.session_state:

    st.session_state.metadata = {}


generate_button = st.button(

    "✨ Generate Document",

    type="primary",

    use_container_width=True
)


if generate_button:

    if (
        not parties.strip()
        or not terms.strip()
    ):

        st.error(
            "Please enter the parties "
            "and at least one term."
        )

    else:

        payload = {

            "document_type":
                document_type,

            "parties":
                parties,

            "terms":
                terms,

            "effective_date":
                effective_date.isoformat(),

            "jurisdiction":
                jurisdiction,

            "additional_instructions":
                additional_instructions
        }


        try:

            with st.spinner(
                "Generating your document..."
            ):

                response = requests.post(

                    f"{BACKEND_URL}/generate",

                    json=payload,

                    timeout=120
                )


            if response.ok:

                result = response.json()

                st.session_state.document_text = (
                    result["text"]
                )

                st.session_state.metadata = payload

                st.session_state.metadata[
                    "model"
                ] = result["model"]

                st.session_state.metadata[
                    "warning"
                ] = result.get("warning")

                st.success(
                    "Document generated successfully!"
                )

            else:

                try:

                    detail = response.json().get(
                        "detail",
                        response.text
                    )

                except Exception:

                    detail = response.text

                st.error(
                    f"Backend error: {detail}"
                )


        except requests.RequestException as exc:

            st.error(
                "Cannot connect to FastAPI. "
                "Start the backend first."
            )

            st.exception(exc)


if st.session_state.document_text:

    st.divider()

    st.subheader(
        "Editable Document"
    )


    warning = (
        st.session_state
        .metadata
        .get("warning")
    )


    if warning:

        st.info(warning)


    edited_text = st.text_area(

        "Edit the generated text "
        "before exporting",

        value=(
            st.session_state.document_text
        ),

        height=600
    )


    st.session_state.document_text = (
        edited_text
    )


    st.subheader(
        "Preview"
    )


    escaped_text = (

        edited_text

        .replace("&", "&amp;")

        .replace("<", "&lt;")

        .replace(">", "&gt;")
    )


    st.markdown(

        f"""
        <div class="preview">
        {escaped_text}
        </div>
        """,

        unsafe_allow_html=True
    )


    logo_base64 = None


    if logo is not None:

        logo_base64 = (

            "data:"

            + (
                logo.type
                or "image/png"
            )

            + ";base64,"

            + base64.b64encode(
                logo.getvalue()
            ).decode("utf-8")
        )


    export_payload = {

        **st.session_state.metadata,

        "text":
            edited_text,

        "brand_name":
            brand_name,

        "logo_base64":
            logo_base64
    }


    export_payload.pop(
        "model",
        None
    )

    export_payload.pop(
        "warning",
        None
    )


    st.subheader(
        "Download"
    )


    txt_column, docx_column, pdf_column = (
        st.columns(3)
    )


    with txt_column:

        if st.button(
            "⬇️ Prepare TXT",
            use_container_width=True
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/export/txt",

                    json=export_payload,

                    timeout=60
                )


                if response.ok:

                    st.download_button(

                        "Save TXT",

                        data=response.content,

                        file_name=(
                            "legalease_document.txt"
                        ),

                        mime="text/plain",

                        use_container_width=True
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as exc:

                st.error(
                    f"Export failed: {exc}"
                )


    with docx_column:

        if st.button(
            "⬇️ Prepare DOCX",
            use_container_width=True
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/export/docx",

                    json=export_payload,

                    timeout=60
                )


                if response.ok:

                    st.download_button(

                        "Save DOCX",

                        data=response.content,

                        file_name=(
                            "legalease_document.docx"
                        ),

                        mime=(
                            "application/"
                            "vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),

                        use_container_width=True
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as exc:

                st.error(
                    f"Export failed: {exc}"
                )


    with pdf_column:

        if st.button(
            "⬇️ Prepare PDF",
            use_container_width=True
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/export/pdf",

                    json=export_payload,

                    timeout=60
                )


                if response.ok:

                    st.download_button(

                        "Save PDF",

                        data=response.content,

                        file_name=(
                            "legalease_document.pdf"
                        ),

                        mime="application/pdf",

                        use_container_width=True
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as exc:

                st.error(
                    f"Export failed: {exc}"
                )


st.divider()


st.caption(
    "LegalEase is a drafting aid and "
    "does not provide legal advice."
)