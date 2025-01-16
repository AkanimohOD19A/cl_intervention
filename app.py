
from utils_app import *
import streamlit as st

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}
    st.session_state.processing = False
    st.session_state.messages = []

session_id = st.session_state.id

# Load existing documents when the app loads
load_existing_documents()

with st.sidebar:
    st.header("Upload your documents!")
    uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf")

    if uploaded_file:
        try:
            file_path = os.path.join("./resources", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            file_key = uploaded_file.name

            if file_key not in st.session_state.get("file_cache", {}):
                st.session_state.file_cache[file_key] = file_path

            st.success("File uploaded and saved successfully!")
            display_pdf(file_path)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

st.header("Resume Recess! 🚀")
if st.session_state.get("file_cache"):
    with st.expander("Select Document"):
        selected_file_key = st.radio("", list(st.session_state.file_cache.keys()))
        selected_file_path = st.session_state.file_cache[selected_file_key]
else:
    st.write("No documents uploaded yet. Please upload a document to get started.")

job_description = st.text_area("Enter Job Description")
tone = st.selectbox(
    "Select the tone for the cover letter:",
    options=["formal", "semi-formal"],
    index=0
)

col1, col2 = st.columns([3, 1])
with col1:
    cl_gen_button = st.button("Generate Cover Letter")
with col2:
    if st.button("Clear ↺"):
        reset_app()
        st.rerun()

if cl_gen_button and job_description:
    if "selected_file_path" in locals() and job_description:
        with st.spinner("Generating cover letter..."):
            # Extract key resume information
            resume_info = extract_key_information_from_resume(selected_file_path)

            # Generate the cover letter
            cover_letter = generate_cover_letter(resume_info, job_description, tone=tone)

        # st.markdown("### Generated Cover Letter")
        st.text_area("Your Cover Letter:", value=cover_letter, height=400)
    else:
        st.error("Please upload a resume and paste the job description to proceed.")




