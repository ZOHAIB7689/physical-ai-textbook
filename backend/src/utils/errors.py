from fastapi import HTTPException, status
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class APIError(HTTPException):
    """
    Custom API error class for consistent error responses
    """
    def __init__(self, detail: str, status_code: int = 400, error_code: str = "GENERIC_ERROR"):
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": detail
                }
            }
        )
        logger.error(f"APIError: {error_code} - {detail}")


class ValidationError(APIError):
    """
    Error for validation failures
    """
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, error_code="VALIDATION_ERROR")


class NotFoundError(APIError):
    """
    Error for resources not found
    """
    def __init__(self, resource: str, identifier: str = None):
        detail = f"{resource} not found"
        if identifier:
            detail += f": {identifier}"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND, error_code="NOT_FOUND_ERROR")


class UnauthorizedError(APIError):
    """
    Error for unauthorized access
    """
    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED, error_code="UNAUTHORIZED_ERROR")


class ForbiddenError(APIError):
    """
    Error for forbidden access
    """
    def __init__(self, detail: str = "Forbidden access"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN, error_code="FORBIDDEN_ERROR")


def handle_exception(e: Exception, context: str = "") -> Dict[str, Any]:
    """
    General exception handler that logs the error and returns a structured response
    """
    error_msg = f"Error in {context}: {str(e)}"
    logger.exception(error_msg)
    
    return {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "details": str(e) if __name__ != "__main__" else "Internal server error"
        }
    }