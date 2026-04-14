
import pdfplumber

text = ""

with pdfplumber.open("data/medical_book.pdf") as pdf:
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"

with open("data/medical_text.txt","w",encoding="utf-8") as f:
    f.write(text)

print("Text extraction complete.")
