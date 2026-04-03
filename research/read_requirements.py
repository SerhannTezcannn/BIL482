import pypdf
import os

def read_pdf(path, output_file):
    with open(output_file, 'a', encoding='utf-8') as out:
        out.write(f"\n\n--- Reading {os.path.basename(path)} ---\n")
        try:
            reader = pypdf.PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            out.write(text)
            out.write(f"\n\n[End of {os.path.basename(path)}]\n")
            print(f"Successfully read {path}")
        except Exception as e:
            msg = f"Error reading {path}: {e}\n"
            out.write(msg)
            print(msg)

files = [
    r"c:\Users\90506\OneDrive\Masaüstü\bil482\Software Requirements Document copy.pdf"
]

output_path = "requirements_comparison.txt"
if os.path.exists(output_path):
    os.remove(output_path)

for f in files:
    read_pdf(f, output_path)
