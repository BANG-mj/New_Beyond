import PyPDF2

class PDFLoader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def load_pdf(self):
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
