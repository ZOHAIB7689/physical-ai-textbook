# Data Model: Physical AI & Humanoid Robotics Textbook Platform

## Entities

### User
- **Fields**:
  - id: UUID (primary key)
  - email: String (unique, required)
  - password_hash: String (required, hashed)
  - first_name: String (required)
  - last_name: String (required)
  - role: Enum ['student', 'educator', 'admin'] (required, default: 'student')
  - language_preference: Enum ['en', 'ur'] (required, default: 'en')
  - created_at: DateTime (required)
  - updated_at: DateTime (required)
  - last_login_at: DateTime
  - is_active: Boolean (required, default: true)
  - profile_image_url: String (optional)

- **Relationships**:
  - One-to-Many: LearningSession (user_id)
  - One-to-Many: AIInteraction (user_id)

- **Validation rules**:
  - Email must be a valid email format
  - Password must meet minimum complexity requirements (8+ characters)
  - Role must be one of the defined enum values
  - Language preference must be one of the supported languages

### ContentModule
- **Fields**:
  - id: UUID (primary key)
  - title: String (required)
  - description: Text (optional)
  - module_number: Integer (required)
  - slug: String (unique, required)
  - is_published: Boolean (required, default: false)
  - created_at: DateTime (required)
  - updated_at: DateTime (required)
  - published_at: DateTime (optional)

- **Relationships**:
  - One-to-Many: Chapter (module_id)
  - Many-to-Many: User (via UserProgress for tracking completion)

- **Validation rules**:
  - Title must not exceed 200 characters
  - Module number must be unique within the textbook
  - Slug must follow URL-friendly format

### Chapter
- **Fields**:
  - id: UUID (primary key)
  - title: String (required)
  - content: Text (required)
  - content_ur: Text (optional, Urdu translation)
  - chapter_number: Integer (required)
  - module_id: UUID (foreign key to ContentModule, required)
  - slug: String (unique, required)
  - is_published: Boolean (required, default: false)
  - created_at: DateTime (required)
  - updated_at: DateTime (required)
  - published_at: DateTime (optional)
  - estimated_reading_time: Integer (in minutes, optional)

- **Relationships**:
  - Many-to-One: ContentModule (module_id)
  - One-to-Many: LearningSession (chapter_id)
  - One-to-Many: AIInteraction (chapter_id)

- **Validation rules**:
  - Title must not exceed 200 characters
  - Content must be provided in at least one language
  - Chapter number must be unique within a module
  - Module ID must reference an existing ContentModule

### LearningSession
- **Fields**:
  - id: UUID (primary key)
  - user_id: UUID (foreign key to User, required)
  - chapter_id: UUID (foreign key to Chapter, required)
  - start_time: DateTime (required)
  - end_time: DateTime (optional)
  - progress_percentage: Integer (0-100, required, default: 0)
  - last_accessed_page: Integer (default: 1)
  - notes: Text (optional)
  - created_at: DateTime (required)
  - updated_at: DateTime (required)

- **Relationships**:
  - Many-to-One: User (user_id)
  - Many-to-One: Chapter (chapter_id)

- **Validation rules**:
  - Progress percentage must be between 0 and 100
  - Start time must not be in the future

### AIInteraction
- **Fields**:
  - id: UUID (primary key)
  - user_id: UUID (foreign key to User, required)
  - chapter_id: UUID (foreign key to Chapter, optional)
  - query: Text (required)
  - response: Text (required)
  - interaction_type: Enum ['chat', 'question', 'summary', 'explanation'] (required)
  - timestamp: DateTime (required)
  - context_used: JSON (optional, for RAG context)
  - created_at: DateTime (required)

- **Relationships**:
  - Many-to-One: User (user_id)
  - Many-to-One: Chapter (chapter_id, optional)

- **Validation rules**:
  - Query and response must not be empty
  - Interaction type must be one of the defined enum values
  - Timestamp must not be in the future

### TranslationSet
- **Fields**:
  - id: UUID (primary key)
  - entity_type: Enum ['chapter', 'ui_component'] (required)
  - entity_id: UUID (required)
  - language: Enum ['ur'] (required)
  - translated_content: Text (required)
  - status: Enum ['draft', 'reviewed', 'approved'] (required, default: 'draft')
  - reviewed_by: UUID (foreign key to User, optional)
  - created_at: DateTime (required)
  - updated_at: DateTime (required)

- **Relationships**:
  - Many-to-One: User (reviewed_by, optional)

- **Validation rules**:
  - Language must be one of the supported languages
  - Status must be one of the defined enum values
  - Entity type and ID combination must be unique for a language