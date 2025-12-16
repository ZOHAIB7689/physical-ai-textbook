# API Contract: AI Interaction

## Submit Question to RAG Chatbot
- **Endpoint**: `POST /api/ai/chat`
- **Description**: Submit a question to the RAG chatbot and receive an answer
- **Headers**: `Authorization: Bearer <access_token>`
- **Request**:
  - Body:
    ```json
    {
      "question": "string (required)",
      "chapter_id": "UUID (optional, for context)",
      "context": "object (optional, additional context for the AI)"
    }
    ```
- **Response**:
  - 200 OK: Answer returned successfully
    ```json
    {
      "answer": "string",
      "references": [
        {
          "chapter_id": "UUID",
          "chapter_title": "string",
          "section": "string"
        }
      ],
      "confidence": "float (0.0-1.0)"
    }
    ```
  - 400 Bad Request: Invalid input data

## Get AI Interaction History
- **Endpoint**: `GET /api/ai/history`
- **Description**: Retrieve the user's AI interaction history
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**:
  - 200 OK: Interaction history returned
    ```json
    {
      "interactions": [
        {
          "id": "UUID",
          "query": "string",
          "response": "string",
          "timestamp": "DateTime",
          "interaction_type": "enum [chat, question, summary, explanation]",
          "chapter_id": "UUID (optional)"
        }
      ]
    }
    ```
  - 401 Unauthorized: Invalid or expired token

## Get Personalized Learning Path
- **Endpoint**: `GET /api/ai/learning-path`
- **Description**: Get AI-recommended learning path based on user progress
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**:
  - 200 OK: Personalized learning path returned
    ```json
    {
      "recommended_chapters": [
        {
          "id": "UUID",
          "title": "string",
          "module_title": "string",
          "reason": "string",
          "priority": "enum [low, medium, high]"
        }
      ],
      "learning_goals": [
        {
          "id": "UUID",
          "title": "string",
          "status": "enum [not_started, in_progress, completed]"
        }
      ],
      "progress_summary": {
        "completed_modules": "integer",
        "completed_chapters": "integer",
        "estimated_completion_time": "string"
      }
    }
    ```
  - 401 Unauthorized: Invalid or expired token

## Submit Query for Content Summary
- **Endpoint**: `POST /api/ai/summary`
- **Description**: Request a summary of a specific chapter or section
- **Headers**: `Authorization: Bearer <access_token>`
- **Request**:
  - Body:
    ```json
    {
      "chapter_id": "UUID (required)",
      "section": "string (optional, specific section to summarize)",
      "detail_level": "enum [brief, medium, detailed] (optional, default: medium)"
    }
    ```
- **Response**:
  - 200 OK: Summary returned
    ```json
    {
      "summary": "string",
      "key_points": ["string"],
      "time_to_read": "integer (estimated time in minutes)"
    }
    ```
  - 400 Bad Request: Invalid input data