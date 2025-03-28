import PyPDF2
import docx


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text.strip()


def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])


def extract_text_from_txt(file):
    return file.read().decode('utf-8', errors='ignore').strip()


def extract_data(file, filename):
    extension = filename.rsplit('.', 1)[-1].lower()

    if extension == 'pdf':
        return extract_text_from_pdf(file)
    elif extension == 'docx':
        return extract_text_from_docx(file)
    elif extension == 'txt':
        return extract_text_from_txt(file)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

