import os
import tempfile
import shutil
import unittest.mock as mock
import numpy as np
import pytest

from backend.services.vector_service import VectorService, local_split_text, SimpleCollection

def test_local_split_text():
    """
    Test that the custom text splitter chunks documents properly on boundaries and handles overlaps.
    """
    text = "Paragraph one is short.\n\nParagraph two is slightly longer and contains multiple sentences. Here is another sentence to fill up space."
    
    # Split with small size
    chunks = local_split_text(text, chunk_size=50, chunk_overlap=10)
    
    assert len(chunks) > 0
    assert chunks[0].startswith("Paragraph one")
    for chunk in chunks:
        assert len(chunk) <= 70  # Safe upper limit including paragraph additions

def test_vector_service_offline():
    """
    Test VectorService indexing, search, and delete operations in offline mode using mock embeddings.
    """
    # Create temporary directory for persistent client
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Mock the embedding function so it doesn't query Gemini API
        mock_embedding = [0.1] * 768
        mock_embedding[0] = 0.9 # Distinguishing dimension
        
        with mock.patch("backend.services.vector_service.GeminiEmbeddingFunction") as MockEmbClass:
            # Setup mock instance behavior
            mock_emb_instance = MockEmbClass.return_value
            mock_emb_instance.side_effect = lambda inputs: [mock_embedding] * len(inputs)
            
            service = VectorService(persist_dir=temp_dir)
            service.api_key = "test_key"
            
            # 1. Test adding document
            paper_id = "test_paper_1"
            title = "Test Paper Title"
            text = "This is the content of the paper that will be chunked and indexed into the mock database."
            
            service.add_paper_document(paper_id=paper_id, title=title, text=text)
            
            # Verify file was created
            persist_file = os.path.join(temp_dir, "research_papers_collection.json")
            assert os.path.exists(persist_file)
            
            # 2. Test similarity search
            hits = service.similarity_search(query="indexed content", paper_ids=[paper_id], n_results=1)
            
            assert len(hits) == 1
            assert hits[0]["metadata"]["paper_id"] == paper_id
            assert hits[0]["metadata"]["title"] == title
            assert "content of the paper" in hits[0]["document"]
            
            # 3. Test deleting paper chunks
            service.delete_job_data([paper_id])
            
            # Search again, should return empty hits
            hits_after_delete = service.similarity_search(query="indexed content", paper_ids=[paper_id], n_results=1)
            assert len(hits_after_delete) == 0
            
    finally:
        # Clean up temp folder
        shutil.rmtree(temp_dir)
