# BioVault AI: Clinical Pro 🏥

An AI-powered radiology triage application designed to optimize clinical workflows, automate diagnostic classifications, and secure medical history. The platform utilizes a fine-tuned **Vision Transformer (ViT)** for chest X-ray analysis, a local **MongoDB** instance for high-speed metadata querying, and an **Ethereum (Ganache)** blockchain network to provide immutable cryptographic proof of all diagnostic records.

---

## 🛠️ Tech Stack & Key Features

*   **Frontend Interface:** Built entirely with `Streamlit` featuring secure role-based user authentication.
*   **Medical Computer Vision:** Custom preprocessing pipeline using `OpenCV` (Contrast Limited Adaptive Histogram Equalization - CLAHE and high-frequency sharpening filters) to condition raw X-ray signals for the model.
*   **Deep Learning Classifier:** Integration with `Hugging Face Transformers` utilizing a specialized Vision Transformer (`vit-chest-xray`) for rapid diagnostic indexing.
*   **Dual-Ledger Security:**
    *   **MongoDB:** Acts as the high-availability storage layer for indexing full patient histories and operational metadata.
    *   **Web3/Ethereum:** Anchors critical, truncated diagnostic data footprints natively into a local ledger (via Ganache) to ensure zero unauthorized tampering.

---

## 📂 Project Structure

```text
├── app.py                 # Main Streamlit application script
├── requirements.txt       # Python dependencies 
└── README.md              # Project documentation
