# API Contract: Content Management

## Get All Modules
- **Endpoint**: `GET /api/modules`
- **Description**: Retrieve all available textbook modules
- **Response**:
  - 200 OK: List of modules returned
    ```json
    {
      "modules": [
        {
          "id": "UUID",
          "title": "string",
          "description": "string",
          "module_number": "integer",
          "slug": "string",
          "is_published": "boolean"
        }
      ]
    }
    ```

## Get Module by Slug
- **Endpoint**: `GET /api/modules/{slug}`
- **Description**: Retrieve a specific module by its slug
- **Response**:
  - 200 OK: Module details returned
    ```json
    {
      "id": "UUID",
      "title": "string",
      "description": "string",
      "module_number": "integer",
      "slug": "string",
      "is_published": "boolean",
      "chapters": [
        {
          "id": "UUID",
          "title": "string",
          "chapter_number": "integer",
          "slug": "string",
          "is_published": "boolean",
          "estimated_reading_time": "integer"
        }
      ]
    }
    ```
  - 404 Not Found: Module not found

## Get Chapter by Slug
- **Endpoint**: `GET /api/chapters/{slug}`
- **Description**: Retrieve a specific chapter by its slug
- **Headers**: `Authorization: Bearer <access_token>` (optional for guests)
- **Response**:
  - 200 OK: Chapter details returned
    ```json
    {
      "id": "UUID",
      "title": "string",
      "content": "string",
      "content_ur": "string (optional)",
      "chapter_number": "integer",
      "module_id": "UUID",
      "slug": "string",
      "is_published": "boolean",
      "estimated_reading_time": "integer",
      "language_preference": "enum [en, ur] (based on user preference or default)"
    }
    ```
  - 404 Not Found: Chapter not found

## Get Chapter in Specific Language
- **Endpoint**: `GET /api/chapters/{slug}/language/{lang}`
- **Description**: Retrieve a chapter in a specific language
- **Headers**: `Authorization: Bearer <access_token>` (optional for guests)
- **Response**:
  - 200 OK: Chapter in requested language returned
    ```json
    {
      "id": "UUID",
      "title": "string",
      "content": "string",
      "language": "enum [en, ur]",
      "chapter_number": "integer",
      "module_id": "UUID",
      "slug": "string",
      "is_published": "boolean",
      "estimated_reading_time": "integer"
    }
    ```
  - 404 Not Found: Chapter or language not found