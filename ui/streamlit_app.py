import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Financial Multi-Agent Analyzer")

query = st.text_area("Your query:", value="Analyze revenue growth, margins, and debt levels for Google")

if st.button("Run Analysis"):
    try:
        resp = requests.post(f"{API_URL}/analyze", json={"query": query}, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        st.subheader("Mode")
        st.write(data["mode"])

        st.subheader("Final Answer")
        st.write(data["final_answer"])

        if data.get("warnings"):
            st.warning("\n".join(data["warnings"]))

        st.subheader("Agent Outputs")
        for ao in data.get("agent_outputs", []):
            st.markdown(f"### {ao['agent']}")
            st.write(ao["content"])
            if ao.get("sources"):
                st.caption("Sources")
                for s in ao["sources"]:
                    st.write(f"- {s['title']}: {s.get('snippet','')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}\n\nMake sure the FastAPI server is running:\n`uvicorn app.api:app --reload --port 8000`")
