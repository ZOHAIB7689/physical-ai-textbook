# Physical AI & Humanoid Robotics Textbook Platform - Project Hierarchy

This document describes the complete file hierarchy of the Physical AI & Humanoid Robotics textbook platform project.

## Root Directory
```
physical-ai-textbook/
├── .git/
├── .gitignore
├── .qwen/
│   └── commands/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── scripts/
│   └── templates/
├── QWEN.md
├── backend/
│   └── src/
│       ├── ai/
│       │   ├── learning_agent.py
│       │   ├── openai_service.py
│       │   ├── progress_analyzer.py
│       │   └── rag_service.py
│       ├── api/
│       │   ├── ai.py
│       │   ├── chapters.py
│       │   ├── content_management.py
│       │   ├── main.py
│       │   └── modules.py
│       ├── auth/
│       │   └── auth.py
│       ├── database/
│       │   └── database.py
│       ├── models/
│       │   ├── ai_interaction.py
│       │   ├── chapter.py
│       │   ├── content_history.py
│       │   ├── content_module.py
│       │   ├── learning_goal.py
│       │   ├── learning_session.py
│       │   ├── translation_set.py
│       │   └── user.py
│       ├── services/
│       │   ├── adaptive_content_service.py
│       │   ├── ai_interaction_service.py
│       │   ├── bulk_content_service.py
│       │   ├── chapter_service.py
│       │   ├── content_history_service.py
│       │   ├── content_management_service.py
│       │   ├── learning_goal_service.py
│       │   ├── learning_path_service.py
│       │   ├── learning_session_service.py
│       │   ├── translation_qa_service.py
│       │   ├── translation_service.py
│       │   ├── translation_workflow.py
│       │   └── user_service.py
│       └── utils/
│           ├── errors.py
│           └── logger.py
├── docs/
│   └── api.md
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Chatbot/
│       │   │   └── Chatbot.js
│       │   ├── ChapterReader/
│       │   │   └── ChapterReader.js
│       │   ├── ContentManagement/
│       │   │   └── ContentManagement.js
│       │   ├── ContentNavigator/
│       │   │   └── ContentNavigator.js
│       │   ├── LanguageSwitcher/
│       │   │   └── LanguageSwitcher.js
│       │   └── LearningAgent/
│       │       └── LearningAgent.js
│       ├── context/
│       │   └── PersonalizationContext.js
│       ├── pages/
│       │   └── textbook.js
│       ├── services/
│       │   ├── contentCache.js
│       │   ├── learningSessionService.js
│       │   └── personalizationService.js
│       ├── styles/
│       │   └── accessibility.css
│       └── utils/
│           ├── accessibilityUtils.js
│           └── i18n.js
├── history/
│   └── prompts/
│       ├── ai-textbook-platform/
│       │   ├── 1-create-system-specification.spec.prompt.md
│       │   ├── 1-create-implementation-plan.plan.prompt.md
│       │   ├── 1-generate-implementation-tasks.tasks.prompt.md
│       │   └── 2-execute-implementation-plan.green.prompt.md
│       └── constitution/
│           └── 1-update-project-constitution.constitution.prompt.md
├── node_modules/
├── specs/
│   └── 001-ai-textbook-platform/
│       ├── checklists/
│       │   └── requirements.md
│       ├── contracts/
│       │   ├── ai-api.md
│       │   ├── content-api.md
│       │   └── user-api.md
│       ├── data-model.md
│       ├── plan.md
│       ├── quickstart.md
│       ├── research.md
│       └── spec.md
├── package.json
├── requirements.txt
├── next.config.js
├── sidebar.js
└── docusaurus.config.js
```

## Directory Descriptions

### Root Level
- `.git/` - Git repository metadata
- `.gitignore` - Files and directories to be ignored by Git
- `.qwen/` - Qwen agent-specific configuration files
- `.specify/` - Specification system configuration and templates
- `QWEN.md` - Main project context file
- `package.json` - Frontend dependencies and configurations
- `requirements.txt` - Backend Python dependencies

### Backend Layer (`backend/`)
Contains the Python/FastAPI backend implementation:
- `ai/` - AI-related services for RAG, learning agents, etc.
- `api/` - API route definitions (endpoints)
- `auth/` - Authentication and authorization logic
- `database/` - Database connection and configuration
- `models/` - SQLAlchemy database models
- `services/` - Business logic services
- `utils/` - Utility functions

### Frontend Layer (`frontend/`)
Contains the React/Next.js frontend implementation:
- `components/` - Reusable UI components
- `context/` - React context providers
- `pages/` - Main page components
- `services/` - Client-side service utilities
- `styles/` - CSS styling files
- `utils/` - Frontend utility functions

### Specification Layer (`specs/`)
Contains all project specifications:
- `001-ai-textbook-platform/` - Main feature specifications
- `checklists/` - Quality validation checklists
- `contracts/` - API contracts and specifications

### Documentation (`docs/`)
Contains API documentation and other docs

### History (`history/`)
Contains prompt history records from the development process