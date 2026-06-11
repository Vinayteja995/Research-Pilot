import os
import json
from typing import List, Dict, Any, Optional
import numpy as np

# Fallback ChromaDB Mock implementation using pure Python + NumPy
try:
    import chromadb
    from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    # Define placeholder classes for local execution
    class EmbeddingFunction:
        pass
    Documents = List[str]
    Embeddings = List[List[float]]

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        self.model_name = model_name
        self.api_key = api_key
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
    def __call__(self, input: Documents) -> Embeddings:
        import google.generativeai as genai
        embeddings = []
        for text in input:
            try:
                truncated_text = text[:8000]
                res = genai.embed_content(
                    model=self.model_name,
                    contents=truncated_text,
                    task_type="retrieval_document"
                )
                embeddings.append(res['embedding'])
            except Exception as e:
                print(f"Embedding error with model {self.model_name}: {e}. Retrying with models/embedding-001...")
                try:
                    res = genai.embed_content(
                        model="models/embedding-001",
                        contents=truncated_text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(res['embedding'])
                except Exception as e2:
                    print(f"Fallback embedding also failed: {e2}. Appending dummy dimensions.")
                    embeddings.append([0.0] * 768)
        return embeddings


class SimpleCollection:
    """
    Pure Python vector database collection with cosine similarity search using NumPy.
    Saves to a local JSON file in the vector DB folder.
    """
    def __init__(self, name: str, embedding_function: GeminiEmbeddingFunction, persist_dir: str):
        self.name = name
        self.embedding_function = embedding_function
        self.persist_file = os.path.join(persist_dir, f"{name}_collection.json")
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.persist_file):
            try:
                with open(self.persist_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load vector fallback database: {e}")
                return {}
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.persist_file), exist_ok=True)
        try:
            with open(self.persist_file, "w") as f:
                json.dump(self.data, f)
        except Exception as e:
            print(f"Failed to persist fallback database: {e}")

    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        embeddings = self.embedding_function(documents)
        for i, doc_id in enumerate(ids):
            self.data[doc_id] = {
                "id": doc_id,
                "document": documents[i],
                "metadata": metadatas[i] if metadatas else {},
                "embedding": embeddings[i]
            }
        self._save()

    def query(self, query_texts: List[str], n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.data:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        # Compute query embedding
        query_embeddings = self.embedding_function(query_texts)
        q_emb = np.array(query_embeddings[0])
        
        candidates = []
        for doc_id, item in self.data.items():
            # Apply metadata filter ($in or exact matching)
            if where:
                match = True
                for k, v in where.items():
                    if isinstance(v, dict) and "$in" in v:
                        if item["metadata"].get(k) not in v["$in"]:
                            match = False
                    else:
                        if item["metadata"].get(k) != v:
                            match = False
                if not match:
                    continue
            
            doc_emb = np.array(item["embedding"])
            # Calculate cosine distance (1.0 - cosine similarity)
            norm_q = np.linalg.norm(q_emb)
            norm_d = np.linalg.norm(doc_emb)
            if norm_q > 0 and norm_d > 0:
                cosine_sim = np.dot(q_emb, doc_emb) / (norm_q * norm_d)
                distance = float(1.0 - cosine_sim)
            else:
                distance = 1.0
                
            candidates.append((distance, item))
            
        # Sort by distance (ascending)
        candidates.sort(key=lambda x: x[0])
        top_hits = candidates[:n_results]
        
        return {
            "ids": [[h[1]["id"] for h in top_hits]],
            "documents": [[h[1]["document"] for h in top_hits]],
            "metadatas": [[h[1]["metadata"] for h in top_hits]],
            "distances": [[h[0] for h in top_hits]]
        }

    def delete(self, where: Optional[Dict[str, Any]] = None):
        if not where:
            self.data = {}
        else:
            to_delete = []
            for doc_id, item in self.data.items():
                match = True
                for k, v in where.items():
                    if isinstance(v, dict) and "$in" in v:
                        if item["metadata"].get(k) not in v["$in"]:
                            match = False
                    else:
                        if item["metadata"].get(k) != v:
                            match = False
                if match:
                    to_delete.append(doc_id)
            for doc_id in to_delete:
                del self.data[doc_id]
        self._save()


def local_split_text(text: str, chunk_size: int = 1500, chunk_overlap: int = 200) -> List[str]:
    """
    Pure Python character-level text splitter that recursively segments document text.
    Handles boundaries and overlaps cleanly.
    """
    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""
    
    for para in paragraphs:
        para_strip = para.strip()
        if not para_strip:
            continue
            
        # If adding paragraph is within limits
        if len(current_chunk) + len(para_strip) <= chunk_size:
            current_chunk += para_strip + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If paragraph itself exceeds size, split it into word groups
            if len(para_strip) > chunk_size:
                words = para_strip.split(" ")
                curr_word_chunk = ""
                for word in words:
                    if len(curr_word_chunk) + len(word) <= chunk_size:
                        curr_word_chunk += word + " "
                    else:
                        if curr_word_chunk:
                            chunks.append(curr_word_chunk.strip())
                        # Standard overlap implementation
                        curr_word_chunk = curr_word_chunk[-chunk_overlap:] if len(curr_word_chunk) > chunk_overlap else ""
                        curr_word_chunk += word + " "
                current_chunk = curr_word_chunk
            else:
                current_chunk = para_strip + "\n\n"
                
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks


class VectorService:
    def __init__(self, persist_dir: str = "backend/chroma_db"):
        self.persist_dir = persist_dir
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        
        if HAS_CHROMADB:
            try:
                self.client = chromadb.PersistentClient(path=self.persist_dir)
                self.use_fallback = False
                print("ChromaDB persistent client loaded successfully.")
            except Exception as e:
                print(f"Failed to load ChromaDB client ({e}). Falling back to LocalVectorDB.")
                self.use_fallback = True
        else:
            self.use_fallback = True
            print("Using pure Python + NumPy LocalVectorDB client.")

    def _get_embedding_fn(self) -> GeminiEmbeddingFunction:
        if not self.api_key:
            self.api_key = os.environ.get("GEMINI_API_KEY", "")
        return GeminiEmbeddingFunction(api_key=self.api_key)

    def add_paper_document(self, paper_id: str, title: str, text: str):
        """
        Chunk and index a paper's text. Supports native ChromaDB or fallback implementation.
        """
        # Split paper text using local character text splitter
        chunks = local_split_text(text, chunk_size=1500, chunk_overlap=200)
        
        emb_fn = self._get_embedding_fn()
        ids = [f"{paper_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"paper_id": paper_id, "title": title, "chunk_index": i} for i in range(len(chunks))]
        
        if not self.use_fallback:
            try:
                collection = self.client.get_or_create_collection(
                    name="research_papers",
                    embedding_function=emb_fn
                )
                # ChromaDB add
                batch_size = 100
                for i in range(0, len(ids), batch_size):
                    collection.add(
                        ids=ids[i:i+batch_size],
                        documents=chunks[i:i+batch_size],
                        metadatas=metadatas[i:i+batch_size]
                    )
                print(f"Indexed {len(chunks)} chunks in ChromaDB for: {title} ({paper_id})")
                return
            except Exception as e:
                print(f"ChromaDB write error ({e}). Attempting fallback database.")
                self.use_fallback = True

        # Pure Python Fallback execution
        collection = SimpleCollection(
            name="research_papers",
            embedding_function=emb_fn,
            persist_dir=self.persist_dir
        )
        collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        print(f"Indexed {len(chunks)} chunks in LocalVectorDB for: {title} ({paper_id})")

    def similarity_search(self, query: str, paper_ids: Optional[List[str]] = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the indexed chunks using cosine similarity.
        """
        emb_fn = self._get_embedding_fn()
        
        where = None
        if paper_ids:
            if len(paper_ids) == 1:
                where = {"paper_id": paper_ids[0]}
            else:
                where = {"paper_id": {"$in": paper_ids}}
                
        if not self.use_fallback:
            try:
                collection = self.client.get_or_create_collection(
                    name="research_papers",
                    embedding_function=emb_fn
                )
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where
                )
                
                hits = []
                if results and results['documents']:
                    for i in range(len(results['documents'][0])):
                        hits.append({
                            "id": results['ids'][0][i],
                            "document": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                            "distance": float(results['distances'][0][i]) if results['distances'] else 0.0
                        })
                return hits
            except Exception as e:
                print(f"ChromaDB query failed ({e}). Retrying with fallback database.")
                self.use_fallback = True

        # Fallback query
        collection = SimpleCollection(
            name="research_papers",
            embedding_function=emb_fn,
            persist_dir=self.persist_dir
        )
        results = collection.query(query_texts=[query], n_results=n_results, where=where)
        
        hits = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                hits.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        return hits

    def delete_job_data(self, paper_ids: List[str]):
        """
        Delete chunks matching specified paper_ids.
        """
        emb_fn = self._get_embedding_fn()
        
        if not self.use_fallback:
            try:
                collection = self.client.get_or_create_collection(
                    name="research_papers",
                    embedding_function=emb_fn
                )
                for pid in paper_ids:
                    collection.delete(where={"paper_id": pid})
                return
            except Exception as e:
                print(f"ChromaDB delete failed ({e}). Switching to fallback.")
                self.use_fallback = True

        # Fallback delete
        collection = SimpleCollection(
            name="research_papers",
            embedding_function=emb_fn,
            persist_dir=self.persist_dir
        )
        for pid in paper_ids:
            collection.delete(where={"paper_id": pid})
