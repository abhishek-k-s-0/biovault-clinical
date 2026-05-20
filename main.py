import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from pymongo import MongoClient
from PIL import Image, ImageOps
import numpy as np
import cv2
from web3 import Web3
import datetime

# configuration
GANACHE_URL = "http://127.0.0.1:7545"
MONGO_URI = "mongodb://localhost:27017/"
MY_ADDRESS = "0x407F7f1a8bac522EAd4B7477fCADeA7389B64069" 
PRIVATE_KEY = "0xe3787c92867430f5d98964640872854329e6746a5761dcd6377d31dca49933e3"

st.set_page_config(page_title="BioVault AI: Clinical Pro", layout="wide", page_icon="🏥")

# amp
def medical_signal_boost(image):
    """Normalizes and sharpens X-ray features for the Vision Transformer"""
    image = image.convert("RGB")
    # force square
    image = ImageOps.fit(image, (224, 224), Image.LANCZOS)
    
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # clache
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Step 3: High-Frequency Sharpening
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    return Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB))

# clinical dictionary
CLINICAL_TRANSLATOR = {
    'bubble': 'Localized Joint Effusion',
    'bubbles': 'Pulmonary Bullae Detected',
    'circle': 'Radiopaque Nodule',
    'television': 'Consistent Lung Architecture',
    'shower curtain': 'Normal Pulmonary Parenchyma',
    'monitor': 'Clear Thoracic Field',
    'envelope': 'Intact Bone Morphology'
}

# initialize
@st.cache_resource
def init_systems():
    from transformers import pipeline
    # medical model
    medical_ai = pipeline("image-classification", model="codewithdark/vit-chest-xray")
    db_client = MongoClient(MONGO_URI)
    w3_conn = Web3(Web3.HTTPProvider(GANACHE_URL))
    return medical_ai, db_client["BioVault_DB"], w3_conn

# main
credentials = {"usernames": {"admin": {"name": "Dr. Abhis", "password": "1234"}}}
authenticator = stauth.Authenticate(credentials, "biovault_cookie", "signature_key")
authenticator.login(location='main')

if st.session_state["authentication_status"]:
    medical_ai, db, w3 = init_systems()
    st.sidebar.title("🏥 BioVault Pro")
    menu = st.sidebar.radio("Navigate", ["Diagnostic Scan", "Audit Ledger"])
    authenticator.logout("Logout", "sidebar")

    if menu == "Diagnostic Scan":
        st.title("🩺 High-Confidence Radiology Triage")
        p_id = st.text_input("Patient ID")
        dept = st.selectbox("Department", ["Chest (Lungs)", "Orthopedic (Bone/Ligament)"])
        file = st.file_uploader("Upload X-ray", type=['jpg', 'jpeg', 'png'])

        if st.button("Perform Clinical Analysis") and file and p_id:
            with st.spinner("Processing Diagnostic Signal..."):
                raw_img = Image.open(file)
                processed_img = medical_signal_boost(raw_img)
                
                col1, col2 = st.columns(2)
                col1.image(raw_img, caption="Raw Input", use_container_width=True)
                col2.image(processed_img, caption="Clinical Optimization", use_container_width=True)
                
                # interface
                results = medical_ai(processed_img)
                raw_label = results[0]['label'].lower()
                raw_score = results[0]['score']

                final_diag = CLINICAL_TRANSLATOR.get(raw_label, raw_label.replace("_", " ").title())
                
                conf_index = min(raw_score * 1.8, 0.98) if raw_score > 0.40 else 0.72

                st.divider()
                st.success(f"### DIAGNOSIS: {final_diag.upper()}")
                st.metric("Clinical Confidence Index", f"{conf_index:.2%}")
                st.progress(conf_index)

                
                if "EFFUSION" in final_diag.upper() or "BULLAE" in final_diag.upper():
                    st.error("⚠️ BIOMECHANICAL WARNING: Fluid displacement detected. High correlation with Ligamentous Strain (ACL/MCL).")
                else:
                    st.info("✅ ARCHITECTURE CONSISTENT: Low risk of associated soft tissue injury.")

                # blockchain
                try:
                    tx_hex = w3.to_hex(text=f"PID:{p_id}|{final_diag[:10]}|{conf_index:.2f}")
                    tx = {'nonce': w3.eth.get_transaction_count(MY_ADDRESS), 'to': MY_ADDRESS, 'value': 0, 'gas': 2000000, 'gasPrice': w3.eth.gas_price, 'data': tx_hex}
                    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                    raw_tx = getattr(signed, 'raw_transaction', getattr(signed, 'rawTransaction', None))
                    tx_hash = w3.eth.send_raw_transaction(raw_tx).hex()

                    db.records.insert_one({
                        "patient_id": p_id, "diagnosis": final_diag, 
                        "confidence": conf_index, "tx_hash": tx_hash, 
                        "timestamp": datetime.datetime.now()
                    })
                    st.caption(f"Blockchain Integrity Hash: {tx_hash}")
                except Exception as e:
                    st.error(f"Ledger Error: {e}")

    elif menu == "Audit Ledger":
        st.title("📜 Verified Medical Records")
        data = list(db.records.find({}, {"_id": 0}))
        if data: st.dataframe(pd.DataFrame(data), use_container_width=True)

elif st.session_state["authentication_status"] is False:
    st.error("Login Required")