import os

import streamlit as st

from triage import build_client, triage_ticket


def load_api_key():
    """Read the key from the environment locally, or from Streamlit secrets when deployed."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            key = None
    return key


st.set_page_config(page_title="Support Ticket Triage", page_icon="🎫")
st.title("Support Ticket Triage")
st.write("Paste a customer message. The model returns its category, urgency, and a one-line summary.")

api_key = load_api_key()
if not api_key:
    st.error("No GEMINI_API_KEY found. Add it as a secret or environment variable.")
    st.stop()

ticket = st.text_area("Customer message", height=150,
                      placeholder="e.g. The app crashes when I upload a photo...")

if st.button("Triage", type="primary"):
    if not ticket.strip():
        st.warning("Please enter a message first.")
    else:
        with st.spinner("Classifying..."):
            try:
                result = triage_ticket(build_client(api_key), ticket)
                col1, col2 = st.columns(2)
                col1.metric("Category", result["category"])
                col2.metric("Urgency", result["urgency"])
                st.info(result["summary"])
                with st.expander("Raw output"):
                    st.json(result)
            except Exception as err:
                st.error(f"Could not triage this message: {err}")