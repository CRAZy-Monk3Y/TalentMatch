# --- utils/pdf_reader.py ---
def extract_text_from_pdf(file):
    import fitz  # PyMuPDF

    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    return text
