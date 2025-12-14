# Physical AI & Humanoid Robotics Textbook Platform

This is an AI-native textbook platform for teaching Physical AI & Humanoid Robotics, designed for the Panaversity Hackathon. The platform uses Docusaurus and Next.js for content delivery, with an integrated RAG (Retrieval-Augmented Generation) chatbot for learning assistance.

## Project Structure

```
physical-ai-textbook/
├── backend/                 # Python/FastAPI backend
│   └── src/
│       ├── ai/             # AI services (RAG, learning agent, etc.)
│       ├── api/            # API route definitions
│       ├── auth/           # Authentication logic
│       ├── database/       # Database models and connections
│       ├── models/         # SQLAlchemy database models
│       ├── services/       # Business logic services
│       └── utils/          # Utilities and helpers
├── frontend/               # React/Next.js frontend
│   └── src/
│       ├── components/     # React UI components
│       ├── context/        # React context providers
│       ├── pages/          # Main pages
│       ├── services/       # Client-side services
│       ├── styles/         # CSS styling
│       └── utils/          # Frontend utilities
├── specs/                  # Project specifications
│   └── 001-ai-textbook-platform/
│       ├── contracts/      # API contracts
│       ├── checklists/     # Quality checklists
│       └── ...
├── tests/                  # Test suites
│   └── unit/               # Unit tests
└── docs/                   # Documentation
```

## Running the Application

### Backend Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables (see `.env.example`)
3. Run the backend:
   ```bash
   uvicorn backend.src.api.main:app --reload
   ```

### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```

## Running Tests

To run the unit tests:
```bash
cd tests/unit
python -m pytest test_core_services.py
python -m pytest test_ai_learning_services.py
python -m pytest test_api_endpoints.py
```

## Key Features

1. **AI-Powered Learning Assistant**: RAG chatbot integrated into the textbook UI
2. **Multilingual Support**: Content available in English and Urdu
3. **Personalization**: Learning paths adapted to individual student needs
4. **Content Management**: Tools for educators to manage textbook content
5. **Progress Tracking**: Learning sessions and AI interaction history

## API Endpoints

### Core Endpoints
- `/api/users` - User management (registration, login, profile)
- `/api/modules` - Content module management
- `/api/chapters` - Chapter content retrieval
- `/api/ai` - AI services (chatbot, learning paths, summaries)
- `/api/content-management` - Content management for educators

### Authentication
All endpoints (except registration/login) require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```