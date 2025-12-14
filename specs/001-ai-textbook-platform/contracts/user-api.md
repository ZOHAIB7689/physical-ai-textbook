# API Contract: User Management

## User Registration
- **Endpoint**: `POST /api/users/register`
- **Description**: Register a new user account
- **Request**:
  - Headers: `Content-Type: application/json`
  - Body:
    ```json
    {
      "email": "string (required)",
      "password": "string (required, min 8 chars)",
      "first_name": "string (required)",
      "last_name": "string (required)",
      "language_preference": "enum [en, ur] (optional, default: en)"
    }
    ```
- **Response**:
  - 201 Created: User account created successfully
    ```json
    {
      "id": "UUID",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "language_preference": "enum [en, ur]",
      "created_at": "DateTime"
    }
    ```
  - 400 Bad Request: Invalid input data
  - 409 Conflict: Email already exists

## User Login
- **Endpoint**: `POST /api/users/login`
- **Description**: Authenticate user and return access token
- **Request**:
  - Headers: `Content-Type: application/json`
  - Body:
    ```json
    {
      "email": "string (required)",
      "password": "string (required)"
    }
    ```
- **Response**:
  - 200 OK: Login successful
    ```json
    {
      "access_token": "string (JWT)",
      "user": {
        "id": "UUID",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "language_preference": "enum [en, ur]"
      }
    }
    ```
  - 400 Bad Request: Invalid input data
  - 401 Unauthorized: Invalid credentials

## Get User Profile
- **Endpoint**: `GET /api/users/profile`
- **Description**: Get authenticated user's profile information
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**:
  - 200 OK: User profile returned
    ```json
    {
      "id": "UUID",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "language_preference": "enum [en, ur]",
      "role": "enum [student, educator, admin]",
      "created_at": "DateTime",
      "updated_at": "DateTime"
    }
    ```
  - 401 Unauthorized: Invalid or expired token

## Update User Profile
- **Endpoint**: `PUT /api/users/profile`
- **Description**: Update authenticated user's profile information
- **Headers**: `Authorization: Bearer <access_token>`
- **Request**:
  - Body:
    ```json
    {
      "first_name": "string (optional)",
      "last_name": "string (optional)",
      "language_preference": "enum [en, ur] (optional)"
    }
    ```
- **Response**:
  - 200 OK: Profile updated successfully
  - 400 Bad Request: Invalid input data
  - 401 Unauthorized: Invalid or expired token