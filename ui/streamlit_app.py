import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Financial Multi-Agent Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Financial Multi-Agent Analyzer")
st.markdown("**Enhanced with Needle-in-Haystack & Tabular Data Support**")

# Sidebar with status
with st.sidebar:
    st.header("🔧 System Status")
    
    # Check API status
    try:
        health_resp = requests.get(f"{API_URL}/health", timeout=2)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            st.success("✅ API Connected")
            st.caption(f"Mode: {health_data.get('ui_mode', 'unknown')}")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Not Available")
        st.caption(f"Expected: {API_URL}")
    
    st.divider()
    st.markdown("### 💡 Example Queries")
    
    # Broad Queries
    st.markdown("**🌐 Broad Queries**")
    broad_queries = [
        "Should I invest in AAPL? Consider market data, fundamentals, and risk",
        "Analyze AAPL investment opportunity comprehensively",
        "Is AAPL overvalued or undervalued? Provide comprehensive analysis",
    ]
    for i, example in enumerate(broad_queries):
        if st.button(f"📝 {example[:45]}...", key=f"broad_{i}", use_container_width=True):
            st.session_state.query = example
    
    st.markdown("**🔍 Needle Queries**")
    needle_queries = [
        "According to the latest earnings report, what was Apple's operating income?",
        "What was Microsoft's revenue in FY2023 according to their annual filing?",
        "What is Apple's gross margin reported in the last quarterly filing?",
    ]
    for i, example in enumerate(needle_queries):
        if st.button(f"📝 {example[:45]}...", key=f"needle_{i}", use_container_width=True):
            st.session_state.query = example
    
    st.markdown("**📊 Tabular Data**")
    tabular_queries = [
        "Get current price and market cap for AAPL",
        "Get price data for AAPL from 2024-01-01 to 2024-01-31",
        "What is the historical price and volume for MSFT for the last 90 days?",
    ]
    for i, example in enumerate(tabular_queries):
        if st.button(f"📝 {example[:45]}...", key=f"tabular_{i}", use_container_width=True):
            st.session_state.query = example

# Main query input
query = st.text_area(
    "Your query:", 
    value=st.session_state.get("query", "Analyze revenue growth, margins, and debt levels for Google"),
    height=100,
    help="Ask questions about stocks, financial data, or investment analysis"
)

col1, col2 = st.columns([1, 4])
with col1:
    run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

if run_button and query.strip():
    with st.spinner("🔄 Processing your query through the multi-agent system..."):
        try:
            resp = requests.post(f"{API_URL}/analyze", json={"query": query}, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # Display mode
            mode_badge = "🟢 Live" if data.get("mode") == "live" else "🟡 Demo"
            st.markdown(f"**Mode:** {mode_badge} {data.get('mode', 'unknown')}")

            # Display warnings if any
            if data.get("warnings"):
                for warning in data["warnings"]:
                    st.warning(f"⚠️ {warning}")

            # Final Answer
            st.subheader("📋 Final Answer")
            st.markdown(data.get("final_answer", "No answer provided"))

            # Agent Outputs
            if data.get("agent_outputs"):
                st.subheader("🤖 Agent Outputs")
                
                for ao in data.get("agent_outputs", []):
                    with st.expander(f"📊 {ao['agent']}", expanded=False):
                        st.markdown(ao.get("content", "No content"))
                        
                        # Display sources
                        if ao.get("sources"):
                            st.markdown("**📚 Sources:**")
                            for s in ao["sources"]:
                                with st.container():
                                    st.markdown(f"**{s.get('title', 'Unknown')}**")
                                    if s.get('snippet'):
                                        st.caption(s['snippet'])
                                    if s.get('url'):
                                        st.markdown(f"[🔗 View Source]({s['url']})")
                                    st.divider()

            # Execution time if available
            if data.get("meta", {}).get("execution_time_seconds"):
                st.caption(f"⏱️ Execution time: {data['meta']['execution_time_seconds']}s")

            # Debug / Raw JSON view (helps when user מרגיש שאין נתונים)
            with st.expander("🧪 Debug: Raw response (JSON)", expanded=False):
                st.json(data)

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timeout. The query took too long. Try a simpler query.")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ **Connection Error**\n\nCannot connect to API at `{API_URL}`\n\nMake sure the FastAPI server is running:\n```bash\n./run_api.sh\n```")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ **HTTP Error {e.response.status_code}**\n\n{e.response.text}")
        except Exception as e:
            st.error(f"❌ **Error**: {str(e)}")
            st.exception(e)

elif run_button:
    st.warning("⚠️ Please enter a query first")

# Footer
st.divider()
st.caption("💡 **Tip**: Try asking specific questions (needle queries) or comprehensive analysis (broad queries)")
