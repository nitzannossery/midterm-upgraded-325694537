#!/bin/bash
# Run Streamlit UI

echo "Starting Streamlit UI..."
echo ""

export API_URL=${API_URL:-http://localhost:8000}

streamlit run ui/streamlit_app.py --server.port 8501
