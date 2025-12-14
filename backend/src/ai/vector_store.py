import qdrant_client
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path

# Load environment variables
load_dotenv()

class QdrantConfig:
    """
    Configuration class for Qdrant vector store
    """
    def __init__(self):
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "textbook_content")
        self.cloud_url = os.getenv("QDRANT_CLOUD_URL")  # For cloud instance
        
    def get_client(self) -> qdrant_client.QdrantClient:
        """
        Get Qdrant client instance
        """
        if self.cloud_url and self.api_key:
            # Use cloud instance
            return qdrant_client.QdrantClient(
                url=self.cloud_url,
                api_key=self.api_key,
                prefer_grpc=True
            )
        else:
            # Use local instance
            return qdrant_client.QdrantClient(
                host=self.host,
                port=self.port
            )

class DocumentPayload(BaseModel):
    """
    Model for document payload in Qdrant
    """
    content: str
    title: str
    module_id: str
    chapter_id: str
    section: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class QdrantService:
    """
    Service class for interacting with Qdrant vector store
    """
    def __init__(self):
        self.config = QdrantConfig()
        self.client = self.config.get_client()
        self.collection_name = self.config.collection_name
        
    def create_collection(self, vector_size: int = 1536) -> bool:
        """
        Create a collection in Qdrant for storing textbook content vectors
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create new collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                
                # Create payload index for efficient filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="module_id",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )
                
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="chapter_id",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )
                
                return True
            else:
                print(f"Collection {self.collection_name} already exists")
                return False
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    def insert_vectors(self, 
                      vectors: List[List[float]], 
                      payloads: List[DocumentPayload], 
                      ids: Optional[List[str]] = None) -> bool:
        """
        Insert vectors with payloads into the collection
        """
        try:
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(vectors))]
                
            points = [
                models.PointStruct(
                    id=ids[i],
                    vector=vectors[i],
                    payload={
                        "content": payloads[i].content,
                        "title": payloads[i].title,
                        "module_id": payloads[i].module_id,
                        "chapter_id": payloads[i].chapter_id,
                        "section": payloads[i].section,
                        "metadata": payloads[i].metadata
                    }
                )
                for i in range(len(vectors))
            ]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return True
        except Exception as e:
            print(f"Error inserting vectors: {e}")
            return False
    
    def search(self, 
               query_vector: List[float], 
               limit: int = 10, 
               module_id: Optional[str] = None,
               chapter_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content in the vector store
        """
        try:
            filters = []
            if module_id:
                filters.append(
                    models.FieldCondition(
                        key="module_id",
                        match=models.MatchValue(value=module_id)
                    )
                )
            if chapter_id:
                filters.append(
                    models.FieldCondition(
                        key="chapter_id",
                        match=models.MatchValue(value=chapter_id)
                    )
                )
            
            search_filter = models.Filter(must=filters) if filters else None
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit
            )
            
            return [
                {
                    "id": result.id,
                    "content": result.payload.get("content"),
                    "title": result.payload.get("title"),
                    "module_id": result.payload.get("module_id"),
                    "chapter_id": result.payload.get("chapter_id"),
                    "section": result.payload.get("section"),
                    "metadata": result.payload.get("metadata"),
                    "score": result.score
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    def delete_collection(self) -> bool:
        """
        Delete the entire collection (use with caution!)
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False