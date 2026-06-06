import google.generativeai as genai
import streamlit as st
import os
import pandas as pd
from datetime import datetime
import base64
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

ai_model = genai.GenerativeModel("gemini-2.5-flash-lite")

st.set_page_config(
    page_title="Family Vault AI | Made by Parth",
    page_icon="🔐",
    layout="wide"
)

APP_PASSWORD = "family123"
DOCUMENT_FOLDER = "documents"
DATA_FILE = "documents_data.csv"

os.makedirs(DOCUMENT_FOLDER, exist_ok=True)

required_columns = [
    "File Name", "Owner", "Document Type", "Notes",
    "Upload Date", "Expiry Date", "File Path"
]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=required_columns).to_csv(DATA_FILE, index=False)
else:
    df = pd.read_csv(DATA_FILE)
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    df = df[required_columns]
    df.to_csv(DATA_FILE, index=False)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #312e81);
}

/* Sidebar text */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div {
    color: white !important;
}

/* Logout button background */
[data-testid="stSidebar"] button {
    background-color: white !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

/* Logout button text */
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button div {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# LOGIN PAGE
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🔐 Family Vault AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">A secure, smart and colorful family document vault</div>', unsafe_allow_html=True)
    st.markdown('<div class="creator">Designed & Developed by Parth 🚀</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.markdown("### 👨‍👩‍👧‍👦 Welcome to Your Family Vault")
        st.write("Store Aadhaar, PAN, marksheets, certificates, insurance papers and more in one secure place.")

        password = st.text_input("🔑 Enter Vault Password", type="password")

        if st.button("🚀 Unlock Vault"):
            if password == APP_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Wrong password. Please try again.")

        st.info("Security enabled with password protection.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# MAIN PAGE
st.markdown('<div class="main-title">👨‍👩‍👧‍👦 Family Vault AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Securely manage, search, download and track important family documents</div>', unsafe_allow_html=True)
st.markdown('<div class="creator">Made by Parth | Smart Family Document Manager</div>', unsafe_allow_html=True)

st.sidebar.markdown("""
## 👨‍👩‍👧‍👦 Family Vault
### Made by Parth 🚀
""")

st.sidebar.markdown("### 🔐 Account")

if st.sidebar.button("🚪 Logout", use_container_width=True, type="primary"):
    st.session_state.logged_in = False
    st.rerun()

df = pd.read_csv(DATA_FILE)

today = pd.Timestamp.today().normalize()
soon_date = today + pd.Timedelta(days=60)

expiry_df = df.copy()
expiry_df["Expiry Date"] = pd.to_datetime(expiry_df["Expiry Date"], errors="coerce")

expiring_soon = expiry_df[
    (expiry_df["Expiry Date"].notna()) &
    (expiry_df["Expiry Date"] >= today) &
    (expiry_df["Expiry Date"] <= soon_date)
]

expired_docs = expiry_df[
    (expiry_df["Expiry Date"].notna()) &
    (expiry_df["Expiry Date"] < today)
]

st.markdown("## 📊 Smart Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📁 Total Documents", len(df))
col2.metric("👨‍👩‍👧‍👦 Family Members", df["Owner"].nunique() if len(df) > 0 else 0)
col3.metric("📄 Document Types", df["Document Type"].nunique() if len(df) > 0 else 0)
col4.metric("⚠️ Expiring Soon", len(expiring_soon))

# AI INSIGHTS
st.markdown("""
<div class="ai-card">
<h3>🤖 AI Smart Insights</h3>
<ul>
<li>Keep important identity documents backed up safely.</li>
<li>Check expiry reminders regularly for passport, insurance and driving license.</li>
<li>Use clear notes while uploading documents for faster search.</li>
<li>Delete outdated documents to keep the vault clean.</li>
</ul>
</div>
""", unsafe_allow_html=True)

if len(expired_docs) > 0:
    st.error(f"🚨 {len(expired_docs)} document(s) have already expired.")

if len(expiring_soon) > 0:
    st.warning(f"⚠️ {len(expiring_soon)} document(s) are expiring within 60 days.")

st.markdown("---")

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

if menu == "Upload Document":
    st.header("📤 Upload New Document")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload PDF/Image", type=["pdf", "jpg", "jpeg", "png"])
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

    if st.button("💾 Save Document"):
        if uploaded_file and owner:
            safe_file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
            file_path = os.path.join(DOCUMENT_FOLDER, safe_file_name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            df = pd.read_csv(DATA_FILE)

            new_data = {
                "File Name": safe_file_name,
                "Owner": owner,
                "Document Type": doc_type,
                "Notes": notes,
                "Upload Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Expiry Date": str(expiry_date) if has_expiry else "",
                "File Path": file_path
            }

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)

            st.success("✅ Document saved successfully!")
            st.rerun()
        else:
            st.error("Please upload a file and enter owner name.")

    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Smart Search":
    st.header("🔍 Smart Search")

    df = pd.read_csv(DATA_FILE)

    search = st.text_input(
        "Search anything",
        placeholder="Example: Parth marksheet, passport, insurance, medical report"
    )

    if search:
        search_words = search.lower().split()

        def smart_match(row):
            combined_text = (
                str(row["Owner"]) + " " +
                str(row["Document Type"]) + " " +
                str(row["Notes"]) + " " +
                str(row["File Name"]) + " " +
                str(row["Expiry Date"])
            ).lower()

            return all(word in combined_text for word in search_words)

        results = df[df.apply(smart_match, axis=1)]

        st.write("Search Results:", len(results))

        if len(results) == 0:
            st.info("No matching documents found.")

        for _, row in results.iterrows():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader(row["File Name"])
            st.write("👤 Owner:", row["Owner"])
            st.write("📄 Type:", row["Document Type"])
            st.write("📝 Notes:", row["Notes"])
            st.write("📅 Uploaded:", row["Upload Date"])
            st.write("⏳ Expiry:", row["Expiry Date"] if str(row["Expiry Date"]) != "nan" else "No expiry date")

            file_path = row["File Path"]

            if os.path.exists(file_path):
                if str(row["File Name"]).lower().endswith(("jpg", "jpeg", "png")):
                    st.image(file_path, caption=row["File Name"], use_container_width=True)

                elif str(row["File Name"]).lower().endswith("pdf"):
                    with open(file_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()

                    st.download_button(
                        "⬇️ Download PDF",
                        pdf_bytes,
                        file_name=row["File Name"],
                        mime="application/pdf"
                    )

                    st.info("PDF preview is limited in Streamlit. Use download to view clearly.")

                with open(file_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Document",
                        f,
                        file_name=row["File Name"]
                    )
            else:
                st.error("File not found in documents folder.")

            st.markdown('</div>', unsafe_allow_html=True)
elif menu == "View All Documents":
    st.header("📁 All Stored Documents")
    df = pd.read_csv(DATA_FILE)

    if len(df) == 0:
        st.info("No documents uploaded yet.")
    else:
        st.dataframe(
            df[["File Name", "Owner", "Document Type", "Upload Date", "Expiry Date"]],
            use_container_width=True
        )

elif menu == "Expiry Reminders":
    st.header("📅 Expiry Reminders")

    if len(expired_docs) == 0 and len(expiring_soon) == 0:
        st.success("✅ No expired or soon-expiring documents.")

    if len(expired_docs) > 0:
        st.subheader("🚨 Expired Documents")
        st.dataframe(
            expired_docs[["File Name", "Owner", "Document Type", "Expiry Date"]],
            use_container_width=True
        )

    if len(expiring_soon) > 0:
        st.subheader("⚠️ Expiring Within 60 Days")
        st.dataframe(
            expiring_soon[["File Name", "Owner", "Document Type", "Expiry Date"]],
            use_container_width=True
        )

elif menu == "Vault AI Assistant":
    st.header("🤖 Vault AI Assistant")

    df = pd.read_csv(DATA_FILE)

    st.write("Ask questions about your stored family documents.")

    user_query = st.text_input(
        "Ask Vault AI",
        placeholder="Example: Which documents are expiring soon?"
    )

    if user_query:
        if len(df) == 0:
            st.info("No documents stored yet.")

        else:
            vault_data = df[
                ["File Name", "Owner", "Document Type", "Notes", "Upload Date", "Expiry Date"]
            ].to_string(index=False)

            prompt = f"""
You are Vault AI, a smart assistant for a family document vault.

Use only the document data given below.
Do not make up any document.
Give clear and short answers.

Document Data:
{vault_data}

User Question:
{user_query}

Answer:
"""

            with st.spinner("Vault AI is thinking..."):
                try:
                    response = ai_model.generate_content(prompt)
                    st.success("🤖 Vault AI Answer")
                    st.write(response.text)

                except Exception as e:
                    st.error("AI assistant could not answer right now.")
                    st.code(str(e))
elif menu == "Delete Document":
    st.header("🗑️ Delete Document")
    df = pd.read_csv(DATA_FILE)

    if len(df) == 0:
        st.info("No documents available.")
    else:
        file_to_delete = st.selectbox("Select Document", df["File Name"])
        st.warning("Deleting a document will remove it permanently.")

        if st.button("🗑️ Delete Selected Document"):
            selected_row = df[df["File Name"] == file_to_delete].iloc[0]
            file_path = selected_row["File Path"]

            if os.path.exists(file_path):
                os.remove(file_path)

            df = df[df["File Name"] != file_to_delete]
            df.to_csv(DATA_FILE, index=False)

            st.success("✅ Document deleted successfully!")
            st.rerun()

st.markdown("""
<hr>
<div class="footer">
<h3>🔐 Family Vault AI</h3>
<p>Designed & Developed by <b>Parth</b> 🚀</p>
<p>Secure • Smart • Family Friendly</p>
</div>
""", unsafe_allow_html=True)