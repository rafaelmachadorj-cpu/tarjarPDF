
"""
Streamlit app: Tarjar PDFs (OCR + Regex + Preview)
Save this file as app_streamlit.py
"""
import streamlit as st
import fitz  # PyMuPDF
import re
import tempfile
import pytesseract
from PIL import Image
import io

st.set_page_config(page_title="Tarjar PDFs", page_icon="🕶️", layout="wide")

st.title("🕶️ Ferramenta de Tarja em PDF (com OCR, Regex e Pré-visualização)")

st.markdown("Faça upload de um PDF, visualize, configure os padrões de tarja e baixe o resultado.")

# Upload do arquivo PDF
uploaded_file = st.file_uploader("📤 Envie um arquivo PDF", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    st.success(f"Arquivo carregado: {uploaded_file.name}")

    # Mostrar prévia das páginas originais
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_orig:
        temp_orig.write(pdf_bytes)
        temp_orig.flush()
        orig_doc = fitz.open(temp_orig.name)

        st.subheader("👁️ Pré-visualização (Antes da Tarja)")
        cols = st.columns(min(3, len(orig_doc)))
        for i in range(min(3, len(orig_doc))):
            pix = orig_doc.load_page(i).get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            cols[i].image(img, caption=f"Página {i+1}")
        orig_doc.close()

    # Configurações de tarja
    st.subheader("⚙️ Configurações de Tarja")
    mode = st.radio("Modo de Tarja", ["Texto exato", "Regex", "OCR + Regex"], index=0)

    terms = []
    if mode == "Texto exato":
        terms_input = st.text_area("Digite os termos a serem tarjados (um por linha)")
        if terms_input:
            terms = [t.strip() for t in terms_input.splitlines() if t.strip()]
    else:
        patterns_input = st.text_area("Digite os padrões Regex (um por linha)")
        if patterns_input:
            terms = [t.strip() for t in patterns_input.splitlines() if t.strip()]
        ignore_case = st.checkbox("Ignorar maiúsculas/minúsculas", value=True)

    fill_black = st.checkbox("Preencher tarja com preto sólido", value=True)

    if st.button("🚀 Aplicar Tarja") and terms:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
            temp_input.write(pdf_bytes)
            temp_input.flush()

            doc = fitz.open(temp_input.name)

            progress_bar = st.progress(0)
            for pno in range(doc.page_count):
                page = doc.load_page(pno)

                rects_to_redact = []

                if mode == "Texto exato":
                    for term in terms:
                        found = page.search_for(term)
                        rects_to_redact.extend(found)

                elif mode == "Regex":
                    flags = re.IGNORECASE if ignore_case else 0
                    text = page.get_text("text")
                    for pat in terms:
                        for m in re.finditer(pat, text, flags):
                            matched = m.group(0)
                            rects_to_redact.extend(page.search_for(matched))

                elif mode == "OCR + Regex":
                    st.write(f"🔍 Executando OCR na página {pno + 1}...")
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img)
                    flags = re.IGNORECASE if ignore_case else 0
                    for pat in terms:
                        for m in re.finditer(pat, ocr_text, flags):
                            matched = m.group(0)
                            found = page.search_for(matched)
                            rects_to_redact.extend(found)

                for r in rects_to_redact:
                    if fill_black:
                        page.add_redact_annot(r, fill=(0, 0, 0))
                    else:
                        page.add_redact_annot(r)
                if rects_to_redact:
                    page.apply_redactions()

                progress_bar.progress(int((pno+1)/doc.page_count * 100))

            output_buffer = io.BytesIO()
            doc.save(output_buffer)
            doc.close()

            st.success("✅ Tarjas aplicadas com sucesso!")

            # Exibir prévia pós-tarja
            st.subheader("👁️ Pré-visualização (Depois da Tarja)")
            doc_after = fitz.open(stream=output_buffer.getvalue(), filetype="pdf")
            cols2 = st.columns(min(3, len(doc_after)))
            for i in range(min(3, len(doc_after))):
                pix = doc_after.load_page(i).get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                cols2[i].image(img, caption=f"Página {i+1}")
            doc_after.close()

            st.download_button(
                label="📥 Baixar PDF Tarjado",
                data=output_buffer.getvalue(),
                file_name="tarjado.pdf",
                mime="application/pdf"
            )
