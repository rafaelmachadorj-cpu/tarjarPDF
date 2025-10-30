# Tarjar PDF - Streamlit App

Files:
- app_streamlit.py : Streamlit app
- requirements.txt : Python dependencies

Instructions:
1. Install Tesseract on your system:
   - Ubuntu: sudo apt install tesseract-ocr
   - macOS (Homebrew): brew install tesseract
   - Windows: install from https://github.com/tesseract-ocr/tesseract and add to PATH

2. Create a virtualenv and install requirements:
   pip install -r requirements.txt

3. Run locally:
   streamlit run app_streamlit.py

To deploy to Streamlit Community Cloud:
- Push this repo to GitHub, then connect it in https://share.streamlit.io or the Streamlit Community Cloud dashboard.
