import chromadb
from chromadb.config import Settings
import google.generativeai as genai
import os

# Initialize ChromaDB client
chroma_client = chromadb.Client(Settings(
    anonymized_telemetry=False,
    allow_reset=True
))

# Get or create collection for petitions
petition_collection = chroma_client.get_or_create_collection(
    name="petitions",
    metadata={"description": "Petition embeddings for duplicate detection"}
)

def get_embedding(text: str):
    """Generate embedding using Gemini API."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key, transport='rest')
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        return None

def check_duplicate(title: str, description: str, threshold: float = 0.85):
    """
    Check if a petition is a duplicate using vector similarity.
    
    Args:
        title: Petition title
        description: Petition description
        threshold: Similarity threshold (0.0 to 1.0)
    
    Returns:
        dict with 'is_duplicate' (bool) and 'similar_petitions' (list)
    """
    combined_text = f"{title}\n\n{description}"
    embedding = get_embedding(combined_text)
    
    if not embedding:
        # Fallback: no duplicate detection if embedding fails
        return {"is_duplicate": False, "similar_petitions": []}
    
    try:
        # Query for similar petitions
        results = petition_collection.query(
            query_embeddings=[embedding],
            n_results=5
        )
        
        similar_petitions = []
        is_duplicate = False
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, petition_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i] if 'distances' in results else 1.0
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= threshold:
                    is_duplicate = True
                    similar_petitions.append({
                        'id': petition_id,
                        'similarity': similarity,
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {}
                    })
        
        return {
            "is_duplicate": is_duplicate,
            "similar_petitions": similar_petitions
        }
    
    except Exception as e:
        print(f"Duplicate check failed: {e}")
        return {"is_duplicate": False, "similar_petitions": []}

def add_petition_to_index(petition_id: int, title: str, description: str):
    """Add a petition to the ChromaDB index."""
    combined_text = f"{title}\n\n{description}"
    embedding = get_embedding(combined_text)
    
    if not embedding:
        print(f"Skipping indexing for petition {petition_id} - embedding failed")
        return False
    
    try:
        petition_collection.add(
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[{"title": title, "petition_id": petition_id}],
            ids=[str(petition_id)]
        )
        return True
    except Exception as e:
        print(f"Failed to add petition to index: {e}")
        return False

def remove_petition_from_index(petition_id: int):
    """Remove a petition from the ChromaDB index."""
    try:
        petition_collection.delete(ids=[str(petition_id)])
        return True
    except Exception as e:
        print(f"Failed to remove petition from index: {e}")
        return False
