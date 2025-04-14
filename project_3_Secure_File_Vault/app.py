import streamlit as st
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- Session Setup ---
if "file_store" not in st.session_state:
    st.session_state.file_store = {}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0
if "remaining_chances" not in st.session_state:
    st.session_state.remaining_chances = 3

# --- Simple login system ---
VALID_USERNAME = "admin"
VALID_PASSWORD = "pass123"

# --- Derive Fernet key from passkey ---
def create_fernet_key(passkey: str) -> Fernet:
    password = passkey.encode()
    salt = b'secure-file-vault-salt'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)

# --- Login page ---
def login():
    st.title("🔐 Reauthorization Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.failed_attempts = 0
            st.session_state.remaining_chances = 3
            st.success("🎉 Login successful!")
        else:
            st.error("🚫 Invalid credentials!")

# --- Main Vault App ---
def main_vault():
    st.title("🗄️ Secure File Vault")
    menu = st.sidebar.radio("Select Action", ["📤 Upload File", "🔓 Retrieve File"])

    if menu == "📤 Upload File":
        passkey = st.text_input("Enter passkey to encrypt file", type="password")
        uploaded_file = st.file_uploader("Upload a file (PDF/Image/Doc)", type=["pdf", "png", "jpg", "jpeg", "txt", "docx"])

        if st.button("Encrypt & Store"):
            if uploaded_file and passkey:
                file_data = uploaded_file.read()
                fernet = create_fernet_key(passkey)
                encrypted_data = fernet.encrypt(file_data)
                st.session_state.file_store[uploaded_file.name] = encrypted_data
                st.success(f"✅ File '{uploaded_file.name}' encrypted and stored securely!")
            else:
                st.warning("Please provide both passkey and file.")

    elif menu == "🔓 Retrieve File":
        filename = st.selectbox("Choose file to retrieve", list(st.session_state.file_store.keys()))
        passkey = st.text_input("Enter passkey to decrypt file", type="password")

        if st.button("Retrieve & Preview"):
            encrypted_data = st.session_state.file_store.get(filename)
            try:
                fernet = create_fernet_key(passkey)
                decrypted_data = fernet.decrypt(encrypted_data)
                st.success("✅ File decrypted successfully!")

                st.download_button("📥 Download File", decrypted_data, file_name=filename)


                if filename.endswith(".pdf"):
                    st.download_button("🔍 Open PDF", decrypted_data, file_name=filename, mime="application/pdf")
                    st.components.v1.iframe("data:application/pdf;base64," + base64.b64encode(decrypted_data).decode(), height=500)

                elif filename.endswith((".png", ".jpg", ".jpeg")):
                    st.image(decrypted_data, caption=filename)

                elif filename.endswith(".txt"):
                    st.text(decrypted_data.decode())

                else:
                    st.info("Preview not supported, but you can download it.")
                st.session_state.remaining_chances = 3  # Reset on success
            except InvalidToken:
                st.session_state.failed_attempts += 1
                st.session_state.remaining_chances -= 1
                st.error(f"❌ Invalid passkey! Chances left: {st.session_state.remaining_chances}")
                if st.session_state.failed_attempts >= 3:
                    st.session_state.authenticated = False

# --- Routing ---
if not st.session_state.authenticated:
    login()
else:
    main_vault()
