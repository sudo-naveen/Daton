import streamlit as st
import requests
import os

API_URL = os.getenv("DATON_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Daton - AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.tool-badge {
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.75rem; margin: 2px;
    background: #1e3a5f; color: #60a5fa;
}
.source-badge {
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.75rem; margin: 2px;
    background: #1a332a; color: #4ade80;
}
div[data-testid="stChatMessage"] { padding: 0.5rem 1rem; }
</style>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("Daton")
    st.caption("AI Data Analyst Agent")
    page = st.radio("Navigation", ["AI Analyst", "Documents", "Datasets", "Database"])
    st.divider()
    if st.button("New Conversation"):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()

if page == "AI Analyst":
    st.markdown("### Daton AI Analyst")
    st.caption("Ask questions about your data, documents, and databases")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tools_used"):
                badges = " ".join([f'<span class="tool-badge">{t}</span>' for t in msg["tools_used"]])
                st.markdown(f"**Tools:** {badges}", unsafe_allow_html=True)
            if msg.get("sources"):
                badges = " ".join([f'<span class="source-badge">{s}</span>' for s in msg["sources"]])
                st.markdown(f"**Sources:** {badges}", unsafe_allow_html=True)
            if msg.get("chart_path") and os.path.exists(msg["chart_path"]):
                st.image(msg["chart_path"])

    user_input = st.chat_input("Ask Daton anything...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/chat",
                        json={
                            "message": user_input,
                            "session_id": st.session_state.session_id,
                        },
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.session_id = data["session_id"]
                        st.markdown(data["response"])

                        if data.get("tools_used"):
                            badges = " ".join([f'<span class="tool-badge">{t}</span>' for t in data["tools_used"]])
                            st.markdown(f"**Tools:** {badges}", unsafe_allow_html=True)
                        if data.get("sources"):
                            badges = " ".join([f'<span class="source-badge">{s}</span>' for s in data["sources"]])
                            st.markdown(f"**Sources:** {badges}", unsafe_allow_html=True)
                        if data.get("chart_path") and os.path.exists(data["chart_path"]):
                            st.image(data["chart_path"])

                        assistant_msg = {
                            "role": "assistant",
                            "content": data["response"],
                            "tools_used": data.get("tools_used", []),
                            "sources": data.get("sources", []),
                            "chart_path": data.get("chart_path"),
                        }
                    else:
                        try:
                            detail = resp.json().get("detail", resp.text)
                        except Exception:
                            detail = resp.text
                        error_msg = f"Error: {detail}"
                        st.error(error_msg)
                        assistant_msg = {"role": "assistant", "content": error_msg}
                except requests.ConnectionError:
                    error_msg = "Cannot connect to Daton backend. Start it with: `uvicorn backend.main:app --reload`"
                    st.error(error_msg)
                    assistant_msg = {"role": "assistant", "content": error_msg}
                except requests.Timeout:
                    error_msg = "Request timed out. The query may be too complex."
                    st.error(error_msg)
                    assistant_msg = {"role": "assistant", "content": error_msg}
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    st.error(error_msg)
                    assistant_msg = {"role": "assistant", "content": error_msg}

        st.session_state.messages.append(assistant_msg)
        st.rerun()

elif page == "Documents":
    st.markdown("### Document Manager")
    st.caption("Upload documents for RAG-powered search")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt", "docx", "csv"],
        help="Supported: PDF, TXT, DOCX, CSV (max 50MB)",
    )

    if uploaded_file:
        if st.button("Upload & Index", type="primary"):
            with st.spinner("Processing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    resp = requests.post(f"{API_URL}/api/documents/upload", files=files, timeout=120)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Uploaded {data['filename']} — {data['chunks_indexed']} chunks indexed")
                        st.rerun()
                    else:
                        try:
                            detail = resp.json().get("detail", resp.text)
                        except Exception:
                            detail = resp.text
                        st.error(f"Upload failed: {detail}")
                except requests.ConnectionError:
                    st.error("Backend not available")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.divider()

    try:
        resp = requests.get(f"{API_URL}/api/documents")
        if resp.status_code == 200:
            docs = resp.json().get("documents", [])
            if docs:
                st.markdown(f"**{len(docs)} document(s) indexed**")
                for doc in docs:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{doc['filename']}** — {doc['chunk_count']} chunks, pages: {', '.join(str(p) for p in doc['pages'])}")
                    with col2:
                        if st.button("Delete", key=f"del_doc_{doc['filename']}"):
                            requests.delete(f"{API_URL}/api/documents/{doc['filename']}")
                            st.rerun()
            else:
                st.info("No documents uploaded yet.")
    except requests.ConnectionError:
        st.warning("Backend not available. Start it with: `uvicorn backend.main:app --reload`")

elif page == "Datasets":
    st.markdown("### Dataset Manager")
    st.caption("Upload CSV/Excel files for analysis")

    uploaded_file = st.file_uploader(
        "Upload a dataset",
        type=["csv", "xlsx", "xls"],
        help="Supported: CSV, XLSX, XLS (max 50MB)",
    )

    if uploaded_file:
        if st.button("Upload Dataset", type="primary"):
            with st.spinner("Processing dataset..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    resp = requests.post(f"{API_URL}/api/datasets/upload", files=files)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Uploaded {data['filename']} — {data['rows']} rows, {len(data['columns'])} columns")
                        st.rerun()
                    else:
                        try:
                            detail = resp.json().get("detail", resp.text)
                        except Exception:
                            detail = resp.text
                        st.error(f"Upload failed: {detail}")
                except requests.ConnectionError:
                    st.error("Backend not available")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.divider()

    try:
        resp = requests.get(f"{API_URL}/api/datasets")
        if resp.status_code == 200:
            datasets = resp.json().get("datasets", [])
            if datasets:
                st.markdown(f"**{len(datasets)} dataset(s) available**")
                for ds in datasets:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        cols_preview = ", ".join(ds.get("columns", [])[:5])
                        if len(ds.get("columns", [])) > 5:
                            cols_preview += "..."
                        st.markdown(f"**{ds['filename']}** — {ds.get('rows', '?')} rows, columns: {cols_preview}")
                    with col2:
                        if st.button("Delete", key=f"del_ds_{ds['filename']}"):
                            requests.delete(f"{API_URL}/api/datasets/{ds['filename']}")
                            st.rerun()
            else:
                st.info("No datasets uploaded yet.")
    except requests.ConnectionError:
        st.warning("Backend not available. Start it with: `uvicorn backend.main:app --reload`")

elif page == "Database":
    st.markdown("### Database Configuration")

    tab1, tab2 = st.tabs(["Connection", "Schema"])

    with tab1:
        db_url = st.text_input(
            "Database URL",
            value="sqlite:///./data/daton.db",
            help="SQLite: sqlite:///./data/daton.db | MySQL: mysql+pymysql://user:pass@host:port/dbname",
        )
        if st.button("Test Connection", type="primary"):
            with st.spinner("Testing connection..."):
                try:
                    resp = requests.post(f"{API_URL}/api/database/test", json={"database_url": db_url})
                    if resp.status_code == 200:
                        data = resp.json()
                        if data["status"] == "connected":
                            st.success(data["message"])
                        else:
                            st.error(data["message"])
                    else:
                        st.error("Connection test failed")
                except requests.ConnectionError:
                    st.error("Backend not available")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with tab2:
        if st.button("Load Schema", type="primary"):
            with st.spinner("Loading schema..."):
                try:
                    resp = requests.get(f"{API_URL}/api/database/schema")
                    if resp.status_code == 200:
                        schema = resp.json().get("schema", {})
                        if schema:
                            for table, info in schema.items():
                                st.markdown(f"#### {table}")
                                cols = info["columns"]
                                st.table([{"Column": c["name"], "Type": c["type"], "Nullable": c["nullable"]} for c in cols])
                        else:
                            st.info("No tables found")
                except requests.ConnectionError:
                    st.error("Backend not available")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
