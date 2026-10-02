"""Standardized Error Handling & Structured API Error Schema for Phase 8.2."""

import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import Request, status
from fastapi.responses import JSONResponse


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error classification")
    message: str = Field(..., description="Human-readable safe error summary")
    request_id: str = Field(..., description="Unique request tracing ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Safe non-sensitive error metadata")


class APIErrorResponse(BaseModel):
    error: ErrorDetail

    @classmethod
    def from_exception(
        cls,
        status_code: int,
        code: str,
        message: str,
        path: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> "APIErrorResponse":
        req_id = request_id or f"req_{uuid.uuid4().hex[:8]}"
        detail_dict = dict(details or {})
        if path:
            detail_dict["path"] = path
        return cls(
            error=ErrorDetail(
                code=code,
                message=message,
                request_id=req_id,
                details=detail_dict,
            )
        )


class GeoVerifyException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class DatabaseTimeoutException(GeoVerifyException):
    def __init__(self, message: str = "Database operation timed out."):
        super().__init__(
            code="DATABASE_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


class OCRTimeoutException(GeoVerifyException):
    def __init__(self, message: str = "OCR document processing timed out."):
        super().__init__(
            code="OCR_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


class ResourceExhaustedException(GeoVerifyException):
    def __init__(self, message: str = "Resource limits exceeded (file size, dimensions, or batch size)."):
        super().__init__(
            code="RESOURCE_EXHAUSTED",
            message=message,
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
        )


async def geoverify_exception_handler(request: Request, exc: GeoVerifyException) -> JSONResponse:
    req_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:8]}")
    payload = APIErrorResponse(
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
            request_id=req_id,
            details=exc.details,
        )
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())
