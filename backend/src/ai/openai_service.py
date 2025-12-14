import os
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv
from backend.src.ai.vector_store import QdrantService
from backend.src.services.content_module_service import ContentModuleService
from backend.src.services.chapter_service import ChapterService

# Load environment variables
load_dotenv()

class OpenAIService:
    """
    Service class for interacting with OpenAI API
    """
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.qdrant_service = QdrantService()
        self.content_module_service = ContentModuleService()
        self.chapter_service = ChapterService()
        
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for the given texts using OpenAI API
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            
            return [item.embedding for item in response.data]
        
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 1536 for _ in texts]
    
    def generate_response(self, prompt: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Generate a response using OpenAI's GPT model with optional context
        """
        try:
            # Build the full prompt with context if provided
            full_prompt = prompt
            
            if context:
                context_str = "\n\nRelevant context:\n"
                for item in context:
                    context_str += f"- {item['title']}: {item['content'][:200]}...\n"
                
                full_prompt = context_str + "\n\nQuestion: " + prompt
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant for a Physical AI & Humanoid Robotics textbook. Provide accurate, educational responses based on the textbook content. If the information isn't available in the provided context, politely say you don't have that information."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error processing your request."
    
    def answer_question_with_context(self, question: str, module_id: str = None, chapter_id: str = None) -> Dict[str, Any]:
        """
        Answer a question using RAG approach with vector search for context
        """
        # Get embeddings for the question
        question_embedding = self.get_embeddings([question])[0]
        
        # Search for relevant content in the vector store
        search_results = self.qdrant_service.search(
            query_vector=question_embedding,
            limit=5,
            module_id=module_id,
            chapter_id=chapter_id
        )
        
        # Generate answer using the search results as context
        answer = self.generate_response(question, search_results)
        
        return {
            "answer": answer,
            "references": search_results,
            "confidence": self.calculate_confidence(answer, search_results)
        }
    
    def calculate_confidence(self, answer: str, references: List[Dict[str, Any]]) -> float:
        """
        Calculate a simple confidence score based on answer length and reference count
        """
        if not references or len(references) == 0:
            return 0.3  # Lower confidence if no references
        
        # Simple heuristic for confidence
        confidence = min(0.8, len(references) * 0.2)  # Up to 0.8 based on references
        if len(answer) > 50:  # If answer is substantive
            confidence += 0.2
        return min(1.0, confidence)
    
    def generate_summary(self, content: str, detail_level: str = "medium") -> str:
        """
        Generate a summary of the given content
        """
        detail_prompts = {
            "brief": "Provide a brief 2-3 sentence summary.",
            "medium": "Provide a medium-length summary covering the key points.",
            "detailed": "Provide a detailed summary covering all main points and subpoints."
        }
        
        prompt = f"{detail_prompts.get(detail_level, detail_prompts['medium'])}\n\nContent to summarize:\n{content}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that creates clear, accurate summaries of educational content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Sorry, I encountered an error while generating the summary."