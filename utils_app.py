import gc
import os
import re
import uuid
import base64
import streamlit as st
import cohere
from PyPDF2 import PdfReader

doc_pth = "resources"
documents = os.listdir(doc_pth)
co = cohere.ClientV2(st.secrets["COHERE_KEY"])


def chunk_text(text, chunk_size=2000):
    """
    Splits text into manageable chunks for processing within token limits.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()


def load_existing_documents():
    for file_name in documents:
        file_pth = os.path.join(doc_pth, file_name)
        if os.path.isfile(doc_pth) and file_name.endswith(".pdf"):
            st.session_state.file_cache[file_name] = file_pth


def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="50%" type="application/pdf" style="height:50vh; width:100%"></iframe>"""
    st.markdown(pdf_display, unsafe_allow_html=True)


def extract_key_information_from_resume(file_path):
    # Extract text from the PDF
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() for page in reader.pages)

    # Optionally chunk the text
    chunks = chunk_text(text)

    # Use Cohere chat API to extract key sections
    extracted_info = ""
    for chunk in chunks:
        response = co.chat(
            model="command-r-plus-08-2024",
            messages=[
                {"role": "user", "content": (
                    "Extract the following sections from the resume text:\n"
                    "1. Professional Summary\n2. Key Skills\n3. Work Experience\n4. Education\n\n"
                    f"Resume Text:\n{chunk}\n\nExtracted Information:"
                )}
            ]
        )
        print('-'*50)
        print(response)
        print('-'*10)
        print(type(response))
        print('-'*10)
        print(dir(response))
        print('='*50)

        extracted_info += response.message.content[0].text.strip()

    return clean_response(extracted_info)


def generate_cover_letter(resume_info, job_description, tone="formal"):
    # Validate tone input
    tone_prompt = (
        "Use a formal tone." if tone == "formal" else "Use a semi-formal tone."
    )

    extracted_cl = ""
    response = co.chat(
        model="command-r-plus-08-2024",
        messages=[
            {"role": "user", "content": (
                f"Write a {tone_prompt.lower()} professional cover letter based on the following:\n\n"
                f"Resume Information:\n{resume_info}\n\n"
                f"Job Description:\n{job_description}\n\n"
                "Highlight relevant skills, experiences, and express enthusiasm for the role.\n\nCover Letter:"
            )}
        ]
    )
    extracted_cl += response.message.content[0].text.strip()

    return clean_response(extracted_cl)


def reset_app():
    st.session_state.file_cache = {}
    st.session_state.messages = []
    gc.collect()


def clean_response(response_text):
    if not isinstance(response_text, str):
        raise ValueError("Expected a string input for cleaning.")

    # Remove placeholders like [Your Name]
    response_text = re.sub(r"\[.*?\]", "", response_text)
    # Replace double spaces or line breaks with single spaces
    response_text = re.sub(r"\s+", " ", response_text).strip()
    # Add line breaks after periods for better readability
    response_text = re.sub(r"(?<!\n)(\.\s)", r"\1\n", response_text)

    return response_text
