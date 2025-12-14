import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import tiktoken
from backend.src.ai.vector_store import QdrantService, DocumentPayload
from backend.src.models.content_module import ContentModule
from backend.src.models.chapter import Chapter


class ContentParser:
    """
    Service for parsing and extracting content from textbook materials
    """
    
    def __init__(self):
        self.enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
    def parse_markdown_content(self, content: str) -> Dict[str, Any]:
        """
        Parse markdown content and extract structured information
        """
        # Convert markdown to HTML to extract text
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract all text
        full_text = soup.get_text()
        
        # Extract sections based on headings
        sections = []
        current_section = {"title": "Introduction", "content": ""}
        
        # Split content by markdown headings
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(current_section)
                
                # Start new section
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                current_section = {
                    "title": title,
                    "level": level,
                    "content": ""
                }
            else:
                current_section["content"] += line + "\n"
        
        # Add the last section
        if current_section["content"].strip():
            sections.append(current_section)
        
        return {
            "full_text": full_text,
            "sections": sections,
            "word_count": len(full_text.split()),
            "token_count": len(self.enc.encode(full_text))
        }
    
    def chunk_content(self, content: str, max_tokens: int = 1000) -> List[str]:
        """
        Split content into chunks of specified token size
        """
        tokens = self.enc.encode(content)
        
        if len(tokens) <= max_tokens:
            return [content]
        
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.enc.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks


class ContentIndexer:
    """
    Service for indexing textbook content in the vector store
    """
    
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.parser = ContentParser()
        self.openai_client = None  # Will be initialized in _get_embeddings
        
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for the given texts using OpenAI API
        """
        # Import OpenAI here to avoid dependency issues if not needed
        try:
            import openai
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            
            # Initialize OpenAI client if not already set
            if self.openai_client is None:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is required")
                
                self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Get embeddings
            response = self.openai_client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            
            return [item.embedding for item in response.data]
        
        except ImportError:
            # Fallback: return zero vectors (for testing without OpenAI dependency)
            return [[0.0] * 1536 for _ in texts]
    
    def index_module_content(self, module: ContentModule, chapters: List[Chapter]) -> bool:
        """
        Index all content for a module and its chapters
        """
        try:
            all_chunks = []
            all_payloads = []
            
            for chapter in chapters:
                # Parse the chapter content
                parsed_content = self.parser.parse_markdown_content(chapter.content)
                
                # Create chunks for each section
                for section in parsed_content["sections"]:
                    # Split section content into smaller chunks if needed
                    chunks = self.parser.chunk_content(section["content"], max_tokens=800)
                    
                    for i, chunk in enumerate(chunks):
                        payload = DocumentPayload(
                            content=chunk,
                            title=f"{chapter.title} - {section['title']}",
                            module_id=str(module.id),
                            chapter_id=str(chapter.id),
                            section=section["title"],
                            metadata={
                                "chapter_number": chapter.chapter_number,
                                "module_number": module.module_number,
                                "section_index": i,
                                "original_title": section["title"]
                            }
                        )
                        
                        all_chunks.append(chunk)
                        all_payloads.append(payload)
                
                # If the chapter has Urdu content, index that as well
                if chapter.content_ur:
                    chunks_ur = self.parser.chunk_content(chapter.content_ur, max_tokens=800)
                    
                    for i, chunk in enumerate(chunks_ur):
                        payload = DocumentPayload(
                            content=chunk,
                            title=f"{chapter.title} - Urdu Translation",
                            module_id=str(module.id),
                            chapter_id=str(chapter.id),
                            section="Urdu Translation",
                            metadata={
                                "chapter_number": chapter.chapter_number,
                                "module_number": module.module_number,
                                "language": "ur",
                                "section_index": i
                            }
                        )
                        
                        all_chunks.append(chunk)
                        all_payloads.append(payload)
            
            # Get embeddings for all chunks
            embeddings = self._get_embeddings(all_chunks)
            
            # Generate IDs for the documents
            doc_ids = [f"{chapter.id}_{i}" for i in range(len(all_chunks))]
            
            # Insert vectors into Qdrant
            success = self.qdrant_service.insert_vectors(
                vectors=embeddings,
                payloads=all_payloads,
                ids=doc_ids
            )
            
            return success
        except Exception as e:
            print(f"Error indexing module content: {e}")
            return False
    
    def index_single_chapter(self, module: ContentModule, chapter: Chapter) -> bool:
        """
        Index content for a single chapter
        """
        try:
            # Parse the chapter content
            parsed_content = self.parser.parse_markdown_content(chapter.content)
            
            all_chunks = []
            all_payloads = []
            
            # Create chunks for each section
            for section in parsed_content["sections"]:
                # Split section content into smaller chunks if needed
                chunks = self.parser.chunk_content(section["content"], max_tokens=800)
                
                for i, chunk in enumerate(chunks):
                    payload = DocumentPayload(
                        content=chunk,
                        title=f"{chapter.title} - {section['title']}",
                        module_id=str(module.id),
                        chapter_id=str(chapter.id),
                        section=section["title"],
                        metadata={
                            "chapter_number": chapter.chapter_number,
                            "module_number": module.module_number,
                            "section_index": i,
                            "original_title": section["title"]
                        }
                    )
                    
                    all_chunks.append(chunk)
                    all_payloads.append(payload)
            
            # If the chapter has Urdu content, index that as well
            if chapter.content_ur:
                chunks_ur = self.parser.chunk_content(chapter.content_ur, max_tokens=800)
                
                for i, chunk in enumerate(chunks_ur):
                    payload = DocumentPayload(
                        content=chunk,
                        title=f"{chapter.title} - Urdu Translation",
                        module_id=str(module.id),
                        chapter_id=str(chapter.id),
                        section="Urdu Translation",
                        metadata={
                            "chapter_number": chapter.chapter_number,
                            "module_number": module.module_number,
                            "language": "ur",
                            "section_index": i
                        }
                    )
                    
                    all_chunks.append(chunk)
                    all_payloads.append(payload)
            
            # Get embeddings for all chunks
            embeddings = self._get_embeddings(all_chunks)
            
            # Generate IDs for the documents
            doc_ids = [f"{chapter.id}_{i}" for i in range(len(all_chunks))]
            
            # Insert vectors into Qdrant
            success = self.qdrant_service.insert_vectors(
                vectors=embeddings,
                payloads=all_payloads,
                ids=doc_ids
            )
            
            return success
        except Exception as e:
            print(f"Error indexing single chapter: {e}")
            return False