# Physical AI & Humanoid Robotics Textbook Platform - Project Hierarchy

This document describes the complete file hierarchy of the Physical AI & Humanoid Robotics textbook platform project.

## Root Directory
```
physical-ai-textbook/
├── .github/
│   └── workflows/
├── .gitignore
├── .qwen/
│   └── commands/
├── .specify/
│   ├── memory/
│   ├── scripts/
│   └── templates/
├── QWEN.md
├── backend/
│   ├── .venv/
│   ├── README.md
│   ├── requirements.txt
│   └── src/
│       ├── ai/
│       │   ├── content_indexer.py
│       │   ├── learning_agent.py
│       │   ├── openai_service.py
│       │   ├── progress_analyzer.py
│       │   ├── rag_service.py
│       │   └── vector_store.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── ai.py
│       │   ├── chapters.py
│       │   ├── content_management.py
│       │   ├── main.py
│       │   ├── modules.py
│       │   └── users.py
│       ├── auth/
│       │   └── auth.py
│       ├── database/
│       │   └── database.py
│       ├── models/
│       │   ├── ai_interaction.py
│       │   ├── ai_recommendation_feedback.py
│       │   ├── chapter.py
│       │   ├── content_history.py
│       │   ├── content_module.py
│       │   ├── learning_goal.py
│       │   ├── learning_memory.py
│       │   ├── learning_session.py
│       │   ├── translation_set.py
│       │   └── user.py
│       ├── services/
│       │   └── (service files not listed in detail)
│       └── utils/
│           └── (utility files not listed in detail)
├── docs/
├── frontend/
│   ├── .babelrc
│   ├── .eslintrc.json
│   ├── docusaurus.config.js
│   ├── next.config.js
│   ├── package.json
│   ├── sidebar.js
│   └── src/
│       ├── components/
│       │   ├── ChapterReader/
│       │   ├── Chatbot/
│       │   ├── ContentManagement/
│       │   ├── ContentNavigator/
│       │   ├── LanguageSwitcher/
│       │   └── LearningAgent/
│       ├── context/
│       │   └── (context files not listed in detail)
│       ├── docs/
│       ├── pages/
│       │   └── (page files not listed in detail)
│       ├── services/
│       │   └── (service files not listed in detail)
│       ├── styles/
│       │   └── (style files not listed in detail)
│       └── utils/
│           └── (utility files not listed in detail)
├── history/
│   └── prompts/
│       └── ai-textbook-platform/
│           └── (prompt history files not listed in detail)
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
│       ├── spec.md
│       └── tasks.md
├── summary.md
└── tests/
    └── unit/
        └── (unit test files not listed in detail)
```

## Directory Descriptions

### Root Level
- `.github/` - GitHub workflow configurations
- `.gitignore` - Files and directories to be ignored by Git
- `.qwen/` - Qwen agent-specific configuration files
- `.specify/` - Specification system configuration and templates
- `QWEN.md` - Main project context file
- `hierarchy.md` - Project hierarchy documentation
- `summary.md` - Project summary documentation

### Backend Layer (`backend/`)
Contains the Python/FastAPI backend implementation:
- `.venv/` - Virtual environment (in .gitignore)
- `README.md` - Backend module documentation
- `requirements.txt` - Python dependencies
- `src/` - Backend source code:
  - `ai/` - AI-related services for RAG, learning agents, etc.
  - `api/` - API route definitions (endpoints)
  - `auth/` - Authentication and authorization logic
  - `database/` - Database connection and configuration
  - `models/` - SQLAlchemy database models
  - `services/` - Business logic services
  - `utils/` - Utility functions

### Frontend Layer (`frontend/`)
Contains the Next.js frontend implementation:
- Configuration files (`.babelrc`, `.eslintrc.json`, `docusaurus.config.js`, `next.config.js`, `package.json`, `sidebar.js`)
- `src/` - Frontend source code:
  - `components/` - Reusable UI components
  - `context/` - React context providers
  - `docs/` - Documentation files
  - `pages/` - Main page components
  - `services/` - Client-side service utilities
  - `styles/` - CSS styling files
  - `utils/` - Frontend utility functions

### Specifications (`specs/`)
Contains all project specifications:
- `001-ai-textbook-platform/` - Main feature specifications
  - `checklists/` - Quality validation checklists
  - `contracts/` - API contracts and specifications
  - Other specification documents

### Documentation (`docs/`)
Contains documentation for the project

### History (`history/`)
Contains prompt history records from the development process:
- `prompts/` - Prompt history records organized by feature

### Tests (`tests/`)
Contains project tests:
- `unit/` - Unit tests