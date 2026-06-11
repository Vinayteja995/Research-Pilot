import os
from typing import Dict, Any
from backend.services.pdf_service import PdfService
from backend.services.vector_service import VectorService

def retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Paper Retrieval Agent Node.
    Downloads paper PDFs, extracts text content, and indexes text chunks into the ChromaDB vector store.
    """
    papers = state.get("papers", [])
    print(f"--- PAPER RETRIEVAL AGENT: Downloading and indexing {len(papers)} papers ---")
    
    pdf_service = PdfService()
    vector_service = VectorService()
    
    indexed_papers = []
    
    for paper in papers:
        paper_id = paper.get("id", "")
        pdf_url = paper.get("pdf_url", "")
        title = paper.get("title", "")
        
        if not pdf_url:
            print(f"No PDF URL found for paper '{title}', skipping download.")
            continue
            
        print(f"Processing paper: '{title}'...")
        
        # Download PDF
        local_path = pdf_service.download_pdf(pdf_url, paper_id)
        if not local_path:
            print(f"Could not download PDF for '{title}', skipping indexing.")
            continue
            
        # Extract text
        try:
            raw_text = pdf_service.extract_text_from_pdf(local_path)
            cleaned_text = pdf_service.clean_text(raw_text)
            
            if cleaned_text:
                # Add to Vector DB
                vector_service.add_paper_document(
                    paper_id=paper_id,
                    title=title,
                    text=cleaned_text
                )
                indexed_papers.append(paper)
            else:
                print(f"Extracted empty text for '{title}'")
        except Exception as e:
            print(f"Failed to process/index paper '{title}': {e}")
            
    print(f"Successfully downloaded and indexed {len(indexed_papers)} out of {len(papers)} papers.")
    
    return {
        "status": "summarizing"
    }
