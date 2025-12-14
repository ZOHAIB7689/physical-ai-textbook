"""
Unit tests for the Physical AI & Humanoid Robotics textbook platform
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import os
import sys

# Add the backend src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from models.user import User, UserCreate
from models.chapter import Chapter, ChapterCreate
from models.ai_interaction import AIInteraction, InteractionType
from models.translation_set import TranslationSet, TranslationStatus
from services.user_service import UserService
from services.chapter_service import ChapterService
from services.ai_interaction_service import AIInteractionService
from services.translation_service import TranslationSetService
from database.database import Base


class TestUserService(unittest.TestCase):
    """Test cases for UserService"""
    
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Create UserService instance
        self.user_service = UserService()
        
        # Create a test user
        self.test_user_data = {
            "email": "test@example.com",
            "password": "hashed_password",
            "first_name": "Test",
            "last_name": "User",
            "password_hash": "hashed_password"
        }
    
    def tearDown(self):
        self.db.close()
    
    def test_create_user_success(self):
        """Test successful user creation"""
        user = self.user_service.create_user(self.db, self.test_user_data)
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
    
    def test_get_user_by_email(self):
        """Test retrieving user by email"""
        # Create a user first
        created_user = self.user_service.create_user(self.db, self.test_user_data)
        
        # Retrieve the user
        retrieved_user = self.user_service.get_user_by_email(self.db, "test@example.com")
        
        self.assertEqual(created_user.id, retrieved_user.id)
        self.assertEqual(retrieved_user.email, "test@example.com")
    
    def test_update_user(self):
        """Test updating user information"""
        # Create a user first
        created_user = self.user_service.create_user(self.db, self.test_user_data)
        
        # Update the user
        from models.user import UserUpdate
        update_data = UserUpdate(first_name="Updated", last_name="Name")
        updated_user = self.user_service.update_user(self.db, str(created_user.id), update_data)
        
        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.last_name, "Name")


class TestChapterService(unittest.TestCase):
    """Test cases for ChapterService"""
    
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Create ChapterService instance
        self.chapter_service = ChapterService()
        
        # Create a test chapter
        self.test_chapter_data = {
            "title": "Test Chapter",
            "content": "This is the test chapter content",
            "content_ur": "یہ ٹیسٹ چیپٹر کا مواد ہے",  # Urdu translation
            "chapter_number": 1,
            "module_id": "test_module_id",
            "slug": "test-chapter",
            "is_published": True,
            "estimated_reading_time": 10
        }
    
    def tearDown(self):
        self.db.close()
    
    def test_create_chapter_success(self):
        """Test successful chapter creation"""
        from models.chapter import ChapterCreate
        chapter_data = ChapterCreate(**self.test_chapter_data)
        
        chapter = self.chapter_service.create_chapter(self.db, chapter_data)
        
        self.assertIsNotNone(chapter)
        self.assertEqual(chapter.title, "Test Chapter")
        self.assertTrue(chapter.is_published)
    
    def test_get_chapter_by_slug(self):
        """Test retrieving chapter by slug"""
        from models.chapter import ChapterCreate
        chapter_data = ChapterCreate(**self.test_chapter_data)
        
        # Create a chapter first
        created_chapter = self.chapter_service.create_chapter(self.db, chapter_data)
        
        # Retrieve the chapter
        retrieved_chapter = self.chapter_service.get_chapter_by_slug(self.db, "test-chapter")
        
        self.assertEqual(created_chapter.id, retrieved_chapter.id)
        self.assertEqual(retrieved_chapter.slug, "test-chapter")
    
    def test_update_chapter(self):
        """Test updating chapter information"""
        from models.chapter import ChapterCreate, ChapterUpdate
        chapter_data = ChapterCreate(**self.test_chapter_data)
        
        # Create a chapter first
        created_chapter = self.chapter_service.create_chapter(self.db, chapter_data)
        
        # Update the chapter
        update_data = ChapterUpdate(title="Updated Chapter Title")
        updated_chapter = self.chapter_service.update_chapter(self.db, str(created_chapter.id), update_data)
        
        self.assertEqual(updated_chapter.title, "Updated Chapter Title")


class TestAIInteractionService(unittest.TestCase):
    """Test cases for AIInteractionService"""
    
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Create AIInteractionService instance
        self.ai_service = AIInteractionService()
        
        # Create a test AI interaction
        from models.ai_interaction import AIInteractionCreate
        self.test_interaction_data = AIInteractionCreate(
            user_id="test_user_id",
            chapter_id="test_chapter_id",
            query="What is robotics?",
            response="Robotics is the field of engineering focused on creating robots...",
            interaction_type=InteractionType.question,
            timestamp=datetime.now()
        )
    
    def tearDown(self):
        self.db.close()
    
    def test_create_interaction_success(self):
        """Test successful AI interaction creation"""
        interaction = self.ai_service.create_interaction(self.db, self.test_interaction_data)
        
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.query, "What is robotics?")
        self.assertEqual(interaction.interaction_type, InteractionType.question)
    
    def test_get_interaction_by_user(self):
        """Test retrieving AI interactions by user"""
        # Create an interaction first
        created_interaction = self.ai_service.create_interaction(self.db, self.test_interaction_data)
        
        # Retrieve interactions by user
        interactions = self.ai_service.get_interactions_by_user(self.db, "test_user_id")
        
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions[0].id, created_interaction.id)
    
    def test_update_interaction(self):
        """Test updating AI interaction"""
        # Create an interaction first
        created_interaction = self.ai_service.create_interaction(self.db, self.test_interaction_data)
        
        # Update the interaction
        from models.ai_interaction import AIInteractionUpdate
        update_data = AIInteractionUpdate(response="Updated response about robotics")
        updated_interaction = self.ai_service.update_interaction(self.db, str(created_interaction.id), update_data)
        
        self.assertEqual(updated_interaction.response, "Updated response about robotics")


class TestTranslationService(unittest.TestCase):
    """Test cases for TranslationService"""
    
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Create TranslationSetService instance
        self.translation_service = TranslationSetService()
        
        # Create a test translation
        from models.translation_set import TranslationSetCreate
        self.test_translation_data = TranslationSetCreate(
            entity_type="chapter",
            entity_id="test_entity_id",
            language="ur",
            translated_content="یہ ٹیسٹ کا ترجمہ ہے",
            status=TranslationStatus.draft
        )
    
    def tearDown(self):
        self.db.close()
    
    def test_create_translation_success(self):
        """Test successful translation creation"""
        translation = self.translation_service.create_translation(self.db, self.test_translation_data)
        
        self.assertIsNotNone(translation)
        self.assertEqual(translation.language, "ur")
        self.assertEqual(translation.status, TranslationStatus.draft)
    
    def test_get_translation_by_entity_and_language(self):
        """Test retrieving translation by entity and language"""
        # Create a translation first
        created_translation = self.translation_service.create_translation(self.db, self.test_translation_data)
        
        # Retrieve translation by entity and language
        retrieved_translation = self.translation_service.get_translation_by_entity_and_language(
            self.db, "chapter", "test_entity_id", "ur"
        )
        
        self.assertIsNotNone(retrieved_translation)
        self.assertEqual(retrieved_translation.id, created_translation.id)
    
    def test_update_translation(self):
        """Test updating translation"""
        # Create a translation first
        created_translation = self.translation_service.create_translation(self.db, self.test_translation_data)
        
        # Update the translation
        from models.translation_set import TranslationSetUpdate
        update_data = TranslationSetUpdate(status=TranslationStatus.approved)
        updated_translation = self.translation_service.update_translation(self.db, str(created_translation.id), update_data)
        
        self.assertEqual(updated_translation.status, TranslationStatus.approved)


class TestAuth(unittest.TestCase):
    """Test authentication/authorization functionality"""
    
    @patch('auth.auth.pwd_context')
    def test_verify_password(self, mock_pwd_context):
        """Test password verification"""
        from auth.auth import verify_password
        
        mock_pwd_context.verify.return_value = True
        
        result = verify_password("plain_password", "hashed_password")
        self.assertTrue(result)
        
        mock_pwd_context.verify.assert_called_with("plain_password", "hashed_password")
    
    @patch('auth.auth.pwd_context')
    def test_get_password_hash(self, mock_pwd_context):
        """Test password hashing"""
        from auth.auth import get_password_hash
        
        mock_pwd_context.hash.return_value = "hashed_result"
        
        result = get_password_hash("plain_password")
        self.assertEqual(result, "hashed_result")
        
        mock_pwd_context.hash.assert_called_with("plain_password")


if __name__ == '__main__':
    unittest.main()