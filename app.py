import streamlit as st
import pandas as pd
from datetime import datetime
from cryptography.fernet import Fernet
from supabase import create_client
import google.generativeai as genai
import os
import tempfile

st.set_page_config(
    page_title="Family Vault AI | Secure Edition",
    page_icon="🔐",
    layout="wide"
)

# Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
ENCRYPTION_KEY = st.secrets["ENCRYPTION_KEY"]

BUCKET_NAME = "family-documents"
APP_PASSWORD = "FamilyVault@2026#Secure!Parth"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
fernet = Fernet(ENCRYPTION_KEY.encode())

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash-lite")

# ---------- CSS ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc, #dbeafe, #ede9fe);
}
.main-title {
    text-align:center;
    font-size:48px;
    font-weight:900;
    background: linear-gradient(90deg, #1d4ed8, #7c3aed, #db2777);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.subtitle {
    text-align:center;
    color:#334155;
    font-size:19px;
    margin-bottom:25px;
}
.card {
    background:white;
    color:#111827;
    padding:22px;
    border-radius:18px;
    box-shadow:0 6px 20px rgba(0,0,0,0.12);
    margin-bottom:18px;
}
.creator {
    text-align:center;
    color:#7c3aed;
    font-weight:800;
}
.footer {
    text-align:center;
    color:#475569;
    margin-top:40px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #312e81);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div {
    color: white !important;
}
[data-testid="stSidebar"] button {
    background-color:white !important;
    border-radius:10px !important;
    font-weight:700 !important;
}
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button div {
    color:black !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def get_documents():
    response = supabase.table("documents").select("*").execute()
    data = response.data
    return pd.DataFrame(data) if data else pd.DataFrame(columns=[
        "id", "file_name", "owner", "document_type", "notes",
        "upload_date", "expiry_date", "storage_path"
    ])

def upload_encrypted_file(uploaded_file, storage_path):
    file_bytes = uploaded_file.getvalue()
    encrypted_bytes = fernet.encrypt(file_bytes)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(encrypted_bytes)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            f,
            file_options={"content-type": "application/octet-stream"}
        )

    os.remove(tmp_path)

def download_decrypted_file(storage_path):
    encrypted_bytes = supabase.storage.from_(BUCKET_NAME).download(storage_path)
    decrypted_bytes = fernet.decrypt(encrypted_bytes)
    return decrypted_bytes

def delete_file(storage_path):
    supabase.storage.from_(BUCKET_NAME).remove([storage_path])

# ---------- Login ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🔐 Family Vault AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Secure encrypted document locker for your family</div>', unsafe_allow_html=True)
    st.markdown('<div class="creator">Designed & Developed by Parth 🚀</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔑 Unlock Family Vault")
        password = st.text_input("Enter Password", type="password")

        if st.button("🚀 Login", use_container_width=True):
            if password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Wrong password.")

        st.info("Files are encrypted before cloud storage.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ---------- Main ----------
st.markdown('<div class="main-title">👨‍👩‍👧‍👦 Family Vault AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Encrypted cloud document storage with AI assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="creator">Made by Parth 🚀</div>', unsafe_allow_html=True)

st.sidebar.markdown("## 👨‍👩‍👧‍👦 Family Vault")
st.sidebar.markdown("### Made by Parth 🚀")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

df = get_documents()

today = pd.Timestamp.today().normalize()
soon_date = today + pd.Timedelta(days=60)

expiry_df = df.copy()
if "expiry_date" in expiry_df.columns:
    expiry_df["expiry_date"] = pd.to_datetime(expiry_df["expiry_date"], errors="coerce")
else:
    expiry_df["expiry_date"] = pd.NaT

expiring_soon = expiry_df[
    (expiry_df["expiry_date"].notna()) &
    (expiry_df["expiry_date"] >= today) &
    (expiry_df["expiry_date"] <= soon_date)
]

expired_docs = expiry_df[
    (expiry_df["expiry_date"].notna()) &
    (expiry_df["expiry_date"] < today)
]

st.markdown("## 📊 Secure Dashboard")

c1, c2, c3, c4 = st.columns(4)
c1.metric("📁 Total Documents", len(df))
c2.metric("👨‍👩‍👧‍👦 Family Members", df["owner"].nunique() if len(df) > 0 else 0)
c3.metric("📄 Document Types", df["document_type"].nunique() if len(df) > 0 else 0)
c4.metric("⚠️ Expiring Soon", len(expiring_soon))

st.info("🔐 Secure Mode: Documents are encrypted before being uploaded to private cloud storage.")

if len(expired_docs) > 0:
    st.error(f"🚨 {len(expired_docs)} document(s) have expired.")

if len(expiring_soon) > 0:
    st.warning(f"⚠️ {len(expiring_soon)} document(s) are expiring within 60 days.")

menu = st.sidebar.radio(
    "📌 Choose Option",
    [
        "Upload Document",
        "Smart Search",
        "View All Documents",
        "Expiry Reminders",
        "Vault AI Assistant",
        "Delete Document"
    ]
)

# ---------- Upload ----------
if menu == "Upload Document":
    st.header("📤 Upload Encrypted Document")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload PDF/Image",
        type=["pdf", "jpg", "jpeg", "png"]
    )

    owner = st.text_input("Owner Name")

    doc_type = st.selectbox(
        "Document Type",
        [
            "Aadhaar", "PAN", "Marksheet", "Certificate",
            "Medical Report", "Insurance", "Passport",
            "Driving License", "Property Document", "Other"
        ]
    )

    notes = st.text_area("Notes")
    has_expiry = st.checkbox("This document has an expiry date")

    expiry_date = ""
    if has_expiry:
        expiry_date = st.date_input("Select Expiry Date")

    if st.button("🔐 Encrypt & Save Document"):
        if uploaded_file and owner:
            safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
            storage_path = f"{owner}/{safe_name}.encrypted"

            try:
                upload_encrypted_file(uploaded_file, storage_path)

                supabase.table("documents").insert({
                    "file_name": uploaded_file.name,
                    "owner": owner,
                    "document_type": doc_type,
                    "notes": notes,
                    "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "expiry_date": str(expiry_date) if has_expiry else "",
                    "storage_path": storage_path
                }).execute()

                st.success("✅ Document encrypted and saved securely!")
                st.rerun()

            except Exception as e:
                st.error("Upload failed.")
                st.code(str(e))
        else:
            st.error("Please upload a file and enter owner name.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Smart Search ----------
elif menu == "Smart Search":
    st.header("🔍 Smart Search")

    search = st.text_input(
        "Search anything",
        placeholder="Example: Parth passport, insurance, marksheet"
    )

    if search:
        words = search.lower().split()

        def smart_match(row):
            text = (
                str(row.get("owner", "")) + " " +
                str(row.get("document_type", "")) + " " +
                str(row.get("notes", "")) + " " +
                str(row.get("file_name", "")) + " " +
                str(row.get("expiry_date", ""))
            ).lower()
            return all(word in text for word in words)

        results = df[df.apply(smart_match, axis=1)]

        st.write("Search Results:", len(results))

        if len(results) == 0:
            st.info("No matching documents found.")

        for _, row in results.iterrows():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(row["file_name"])
            st.write("👤 Owner:", row["owner"])
            st.write("📄 Type:", row["document_type"])
            st.write("📝 Notes:", row["notes"])
            st.write("📅 Uploaded:", row["upload_date"])
            st.write("⏳ Expiry:", row["expiry_date"] if row["expiry_date"] else "No expiry date")

            try:
                file_bytes = download_decrypted_file(row["storage_path"])
                st.download_button(
                    "⬇️ Download Decrypted Document",
                    file_bytes,
                    file_name=row["file_name"]
                )

                if str(row["file_name"]).lower().endswith(("jpg", "jpeg", "png")):
                    st.image(file_bytes, caption=row["file_name"], use_container_width=True)

            except Exception as e:
                st.error("Unable to open file.")
                st.code(str(e))

            st.markdown('</div>', unsafe_allow_html=True)

# ---------- View ----------
elif menu == "View All Documents":
    st.header("📁 All Stored Documents")

    if len(df) == 0:
        st.info("No documents uploaded yet.")
    else:
        st.dataframe(
            df[["file_name", "owner", "document_type", "upload_date", "expiry_date"]],
            use_container_width=True
        )

# ---------- Expiry ----------
elif menu == "Expiry Reminders":
    st.header("📅 Expiry Reminders")

    if len(expired_docs) == 0 and len(expiring_soon) == 0:
        st.success("✅ No expired or soon-expiring documents.")

    if len(expired_docs) > 0:
        st.subheader("🚨 Expired Documents")
        st.dataframe(
            expired_docs[["file_name", "owner", "document_type", "expiry_date"]],
            use_container_width=True
        )

    if len(expiring_soon) > 0:
        st.subheader("⚠️ Expiring Within 60 Days")
        st.dataframe(
            expiring_soon[["file_name", "owner", "document_type", "expiry_date"]],
            use_container_width=True
        )

# ---------- AI ----------
elif menu == "Vault AI Assistant":
    st.header("🤖 Vault AI Assistant")

    user_query = st.text_input(
        "Ask Vault AI",
        placeholder="Example: Which documents are expiring soon?"
    )

    if user_query:
        if len(df) == 0:
            st.info("No documents stored yet.")
        else:
            vault_data = df[
                ["file_name", "owner", "document_type", "notes", "upload_date", "expiry_date"]
            ].to_string(index=False)

            prompt = f"""
You are Vault AI, a smart assistant for a family document vault.

Use only the document data below.
Do not make up documents.
Answer clearly and shortly.

Document Data:
{vault_data}

Question:
{user_query}

Answer:
"""

            with st.spinner("Vault AI is thinking..."):
                try:
                    response = ai_model.generate_content(prompt)
                    st.success("🤖 Vault AI Answer")
                    st.write(response.text)
                except Exception as e:
                    st.error("Vault AI error.")
                    st.code(str(e))

# ---------- Delete ----------
elif menu == "Delete Document":
    st.header("🗑️ Delete Document")

    if len(df) == 0:
        st.info("No documents available.")
    else:
        selected = st.selectbox("Select Document", df["file_name"])

        st.warning("Deleting will permanently remove the document from cloud storage.")

        if st.button("🗑️ Delete Selected Document"):
            row = df[df["file_name"] == selected].iloc[0]

            try:
                delete_file(row["storage_path"])
                supabase.table("documents").delete().eq("id", int(row["id"])).execute()

                st.success("✅ Document deleted successfully!")
                st.rerun()

            except Exception as e:
                st.error("Delete failed.")
                st.code(str(e))

st.markdown("""
<hr>
<div class="footer">
<h3>🔐 Family Vault AI - Secure Edition</h3>
<p>Designed & Developed by <b>Parth</b> 🚀</p>
<p>Encrypted • Private • Family Friendly</p>
</div>
""", unsafe_allow_html=True)
