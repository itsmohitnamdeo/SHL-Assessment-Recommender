import streamlit as st
import requests

st.set_page_config(
    page_title="SHL Assessment Recommender",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align:center; color:#4B8BBE;'>🤖 SHL Assessment Recommender</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; font-size:18px; color:#306998;'>Enter a query or a job description and get matching assessments</p>",
    unsafe_allow_html=True
)

query = st.text_area(
    "🔍 Enter your query:",
    placeholder="e.g. Looking for a test to evaluate critical thinking for entry-level hires",
    height=120
)

if st.button("🔎 Get Recommendations"):
    if query.strip():
        try:
            with st.spinner("Fetching recommendations..."):
                res = requests.post(
                    # "https://shl-assessment-recommendation-system-xx1e.onrender.com/recommend",
                    "http://127.0.0.1:8000/recommend", #for localhost
                    json={"query": query},
                    timeout=15
                )

            if res.status_code == 200:
                data = res.json()
                recommended_assessments = data.get("recommended assessments", [])

                if recommended_assessments:
                    st.success(f"Top {len(recommended_assessments)} recommendations found!")

                    # Display as cards
                    for assessment in recommended_assessments:
                        st.markdown("---")
                        cols = st.columns([3, 1])
                        with cols[0]:
                            st.markdown(f"### [{assessment['name']}]({assessment['url']})")
                            st.markdown(f"**Description:** {assessment['description']}")
                            st.markdown(f"**Test Type:** {', '.join(assessment['test_type'])}")
                        with cols[1]:
                            st.markdown(f"**Duration:** {assessment['duration']} min")
                            st.markdown(f"**Adaptive Support:** {assessment['adaptive_support']}")
                            st.markdown(f"**Remote Support:** {assessment['remote_support']}")

                else:
                    st.warning("No recommendations found for this query.")
            else:
                st.error(f"API Error: {res.status_code} - {res.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {e}")
    else:
        st.warning("Please enter a valid query.")
