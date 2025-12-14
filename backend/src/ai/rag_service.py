import os
from typing import List, Dict, Any, Optional
from backend.src.ai.openai_service import OpenAIService
from backend.src.ai.vector_store import QdrantService
from backend.src.services.content_module_service import ContentModuleService
from backend.src.services.chapter_service import ChapterService
from backend.src.services.ai_interaction_service import AIInteractionService
from backend.src.models.ai_interaction import InteractionType
from sqlalchemy.orm import Session


class RAGService:
    """
    Service class for Retrieval-Augmented Generation functionality
    """
    def __init__(self):
        self.openai_service = OpenAIService()
        self.qdrant_service = QdrantService()
        self.content_module_service = ContentModuleService()
        self.chapter_service = ChapterService()
        self.ai_interaction_service = AIInteractionService()
    
    def query_knowledge_base(self, 
                           query: str, 
                           module_id: Optional[str] = None, 
                           chapter_id: Optional[str] = None,
                           max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the knowledge base (vector store) for relevant content
        """
        # Get embedding for the query
        query_embedding = self.openai_service.get_embeddings([query])[0]
        
        # Search in the vector store
        search_results = self.qdrant_service.search(
            query_vector=query_embedding,
            limit=max_results,
            module_id=module_id,
            chapter_id=chapter_id
        )
        
        return search_results
    
    def generate_response_with_rag(self, 
                                 query: str, 
                                 user_id: str, 
                                 module_id: Optional[str] = None, 
                                 chapter_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response using RAG approach (retrieve + generate)
        """
        # Query the knowledge base for relevant content
        context = self.query_knowledge_base(query, module_id, chapter_id)
        
        # Generate response using the retrieved context
        response_data = self.openai_service.answer_question_with_context(query, module_id, chapter_id)
        
        # Create an AI interaction record
        from backend.src.models.ai_interaction import AIInteractionCreate
        from datetime import datetime
        
        interaction_data = AIInteractionCreate(
            user_id=user_id,
            query=query,
            response=response_data["answer"],
            interaction_type=InteractionType.question,
            timestamp=datetime.now()
        )
        
        # Add chapter_id to interaction if provided
        if chapter_id:
            interaction_data.chapter_id = chapter_id
        
        return {
            "answer": response_data["answer"],
            "references": response_data["references"],
            "confidence": response_data["confidence"],
            "interaction_saved": True
        }
    
    def answer_question(self, 
                       question: str, 
                       user_id: str, 
                       module_id: Optional[str] = None, 
                       chapter_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer a question using RAG methodology
        """
        return self.generate_response_with_rag(question, user_id, module_id, chapter_id)
    
    def generate_content_summary(self, 
                               content: str, 
                               detail_level: str = "medium",
                               user_id: str = None) -> str:
        """
        Generate a summary of content using RAG-enhanced generation
        """
        summary = self.openai_service.generate_summary(content, detail_level)
        
        # Optionally save this interaction
        if user_id:
            from backend.src.models.ai_interaction import AIInteractionCreate
            from datetime import datetime
            
            interaction_data = AIInteractionCreate(
                user_id=user_id,
                query=f"Generate {detail_level} summary",
                response=summary,
                interaction_type=InteractionType.summary,
                timestamp=datetime.now()
            )
        
        return summary
    
    def find_related_content(self, 
                           content: str, 
                           module_id: Optional[str] = None, 
                           chapter_id: Optional[str] = None,
                           limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find related content based on the provided content
        """
        # Get embedding for the content
        content_embedding = self.openai_service.get_embeddings([content])[0]
        
        # Search in the vector store
        search_results = self.qdrant_service.search(
            query_vector=content_embedding,
            limit=limit,
            module_id=module_id,
            chapter_id=chapter_id
        )
        
        return search_results