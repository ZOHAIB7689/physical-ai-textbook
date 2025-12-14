# API Documentation

## Overview
This document provides information about the Physical AI & Humanoid Robotics textbook platform's API endpoints.

## Base URL
`https://api.textbook-platform.example.com`

## Authentication
Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### User Management
- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - Authenticate user and return access token
- `GET /api/users/profile` - Get authenticated user's profile information
- `PUT /api/users/profile` - Update authenticated user's profile information

### Content Management
- `GET /api/modules` - Retrieve all available textbook modules
- `GET /api/modules/{slug}` - Retrieve a specific module by its slug
- `GET /api/chapters/{slug}` - Retrieve a specific chapter by its slug
- `GET /api/chapters/{slug}/language/{lang}` - Retrieve a chapter in a specific language

### AI Interaction
- `POST /api/ai/chat` - Submit a question to the RAG chatbot
- `GET /api/ai/history` - Retrieve the user's AI interaction history
- `GET /api/ai/learning-path` - Get AI-recommended learning path based on user progress
- `POST /api/ai/summary` - Request a summary of a specific chapter or section

## Error Handling
API responses follow this structure:
```
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {} // optional additional error details
  }
}
```

## Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error