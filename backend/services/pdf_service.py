import os
import requests
import fitz  # PyMuPDF
from typing import Optional

class PdfService:
    def __init__(self, cache_dir: str = "backend/pdf_cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def download_pdf(self, pdf_url: str, paper_id: str) -> Optional[str]:
        """
        Download a PDF from the arXiv URL and cache it locally.
        Returns the local file path if successful, otherwise None.
        """
        local_filename = f"{paper_id.replace('/', '_')}.pdf"
        local_filepath = os.path.join(self.cache_dir, local_filename)

        # Return cached copy if it exists
        if os.path.exists(local_filepath) and os.path.getsize(local_filepath) > 0:
            return local_filepath

        try:
            print(f"Downloading PDF: {pdf_url}")
            response = requests.get(pdf_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(local_filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return local_filepath
            else:
                print(f"Failed to download PDF, status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Failed to download PDF {pdf_url}: {e}")
            return None

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract plain text from a local PDF using PyMuPDF (fitz).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        text_content = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                # Simple cleanup: separate pages with newlines
                text_content.append(page_text)
            doc.close()
            return "\n\n--- PAGE BREAK ---\n\n".join(text_content)
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            return ""
            
    def clean_text(self, text: str) -> str:
        """
        Simple text cleaning to remove multiple consecutive spaces/newlines.
        """
        if not text:
            return ""
        # Remove extra whitespace and format nicely
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line_stripped = line.strip()
            if line_stripped:
                cleaned_lines.append(line_stripped)
        return "\n".join(cleaned_lines)
