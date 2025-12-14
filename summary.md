# Physical AI & Humanoid Robotics Textbook Platform - API Summary

This document provides a comprehensive overview of all the API endpoints in the Physical AI & Humanoid Robotics textbook platform.

## Backend API Structure

The backend consists of a Python/FastAPI application with the following main API modules:

### 1. Main API (`/api/main.py`)
- **Entry Point**: `backend/src/api/main.py`
- **Purpose**: Central API router that includes other API modules
- **Connected Endpoints**:
  - `/api/users/` (from `users.py`)
  - `/api/modules/` (from `modules.py`)
  - `/api/chapters/` (from `chapters.py`)
  - `/api/ai/` (from `ai.py`)
  - `/api/content-management/` (from `content_management.py`)

### 2. User API (`/api/users.py`)
- **Entry Point**: `backend/src/api/users.py`
- **Base Endpoint**: `/api/users`
- **Endpoints**:
  - `POST /api/users/register` - Register a new user (with email, password, etc.)
  - `POST /api/users/login` - Authenticate and return JWT token
  - `GET /api/users/profile` - Get authenticated user profile
  - `PUT /api/users/profile` - Update user profile information
- **Purpose**: User management and authentication
- **Connected Services**: `UserService` in `backend/src/services/user_service.py`

### 3. Modules API (`/api/modules.py`)
- **Entry Point**: `backend/src/api/modules.py`
- **Base Endpoint**: `/api/modules`
- **Endpoints**:
  - `GET /api/modules` - Get all content modules (with pagination)
  - `GET /api/modules/{module_id}` - Get specific module by ID
  - `GET /api/modules/slug/{slug}` - Get specific module by slug
- **Purpose**: Content module retrieval and management
- **Connected Services**: `ContentModuleService` in `backend/src/services/content_module_service.py`

### 4. Chapters API (`/api/chapters.py`)
- **Entry Point**: `backend/src/api/chapters.py`
- **Base Endpoint**: `/api/chapters`
- **Endpoints**:
  - `GET /api/chapters/{slug}` - Get chapter by slug
  - `GET /api/chapters/module/{module_id}` - Get all chapters in a module
  - `GET /api/chapters/{slug}/language/{lang}` - Get chapter in specific language
- **Purpose**: Chapter content retrieval with language support
- **Connected Services**: `ChapterService` in `backend/src/services/chapter_service.py`

### 5. AI API (`/api/ai.py`)
- **Entry Point**: `backend/src/api/ai.py`
- **Base Endpoint**: `/api/ai`
- **Endpoints**:
  - `GET /api/ai/` - Root endpoint for AI services
  - `POST /api/ai/chat` - Submit question to RAG chatbot
  - `GET /api/ai/history` - Get user's AI interaction history
  - `GET /api/ai/learning-path` - Get personalized learning path
  - `POST /api/ai/summary` - Request content summary
  - `POST /api/ai/recommendation-feedback` - Submit feedback on AI recommendations
  - `GET /api/ai/recommendation-feedback/{recommendation_id}` - Get feedback for specific recommendation
  - `GET /api/ai/recommendation-feedback/{recommendation_id}/aggregate` - Get aggregated feedback stats
- **Purpose**: AI-powered learning assistance and personalization
- **Connected Services**: 
  - `RAGService` in `backend/src/ai/rag_service.py`
  - `LearningAgent` in `backend/src/ai/learning_agent.py`
  - `AIInteractionService` in `backend/src/services/ai_interaction_service.py`
  - `LearningPathService` in `backend/src/services/learning_path_service.py`
  - `AIRecommendationFeedbackService` in `backend/src/services/ai_recommendation_feedback_service.py`

### 6. Content Management API (`/api/content_management.py`)
- **Entry Point**: `backend/src/api/content_management.py`
- **Base Endpoint**: `/api/content-management`
- **Endpoints**:
  - `GET /api/content-management/` - Root endpoint for content management
  - `GET /api/content-management/content-items` - Get content items that need management
  - `POST /api/content-management/translations` - Create new translation
  - `GET /api/content-management/translations` - Get all translations
  - `GET /api/content-management/translations/{entity_type}/{entity_id}/{language}` - Get specific translation
  - `PUT /api/content-management/translations/{translation_id}` - Update specific translation
  - `GET /api/content-management/learning-goals` - Get user's learning goals
  - `POST /api/content-management/learning-goals` - Create new learning goal
  - `GET /api/content-management/learning-goals/{goal_id}` - Get specific learning goal
  - `PUT /api/content-management/learning-goals/{goal_id}` - Update learning goal
  - `DELETE /api/content-management/learning-goals/{goal_id}` - Delete learning goal
- **Purpose**: Content management for educators and administrators
- **Connected Services**:
  - `TranslationSetService` in `backend/src/services/translation_service.py`
  - `LearningGoalService` in `backend/src/services/learning_goal_service.py`

## Connection Flow Between Components

### Data Flow
1. **Frontend** → **API Endpoints** → **Services** → **Models** → **Database**
2. **Frontend** can communicate directly with **AI Services** via API endpoints
3. **AI Services** connect to external services like OpenAI and Qdrant

### Authentication Flow
1. **User Authentication**: `/api/users/login` → Creates JWT token (valid for 30 minutes)
2. **Token Storage**: Token stored in frontend localStorage
3. **Token Verification**: All protected endpoints verify JWT token via `get_current_active_user()` dependency
4. **Authorization**: Role-based access control (student, educator, admin)

### AI Processing Flow
1. **Query Input**: User submits question to `/api/ai/chat`
2. **RAG Processing**: `RAGService` retrieves related content from Qdrant vector store
3. **OpenAI Integration**: `OpenAIService` generates response using OpenAI API
4. **Response Return**: Answer with references returned to frontend
5. **History Logging**: Interaction saved via `AIInteractionService`

### Translation Flow
1. **Content Creation**: Educators create content in `backend/src/models/chapter.py`
2. **Translation Request**: Via `/api/content-management/translations`
3. **Storage**: Translations stored in `TranslationSet` model
4. **Retrieval**: Language-specific content served via `/api/chapters/{slug}/language/{lang}`
5. **Quality Assurance**: `TranslationQualityAssuranceService` validates translations

### Learning Path Flow
1. **Progress Tracking**: `LearningSessionService` tracks user progress
2. **Analysis**: `ProgressAnalyzer` analyzes user behavior
3. **Path Generation**: `LearningPathService` creates personalized path based on analysis
4. **Recommendations**: `LearningAgent` provides adaptive recommendations
5. **Delivery**: `/api/ai/learning-path` endpoint serves personalized path

## Security Considerations
- JWT-based authentication required for all endpoints
- Role-based access control (RBAC) for educator/admin functions
- Rate limiting (5/minute) on AI endpoints to prevent abuse
- Input validation at all API endpoints
- Secure storage of user data in encrypted database

## Performance Optimizations
- Content caching via `ContentCache` in frontend
- Database query optimization with proper indexing
- Asynchronous processing where possible in AI services
- CDN-friendly static assets for faster delivery