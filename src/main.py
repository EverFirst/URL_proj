"""FastAPI application entry point with middleware and exception handlers."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.domain.exceptions import NotFoundError, ValidationError, ConflictError

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="RESTful API for managing URL collections with public sharing capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing information.

    Args:
        request: Incoming HTTP request
        call_next: Next middleware/handler in chain

    Returns:
        HTTP response
    """
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate request duration
    duration = time.time() - start_time

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )

    return response


# Exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle NotFoundError exceptions.

    Args:
        request: HTTP request
        exc: NotFoundError exception

    Returns:
        404 JSON response
    """
    logger.warning(f"Not found: {exc.message}", extra={"path": str(request.url.path)})
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle ValidationError exceptions.

    Args:
        request: HTTP request
        exc: ValidationError exception

    Returns:
        400 JSON response
    """
    logger.warning(f"Validation error: {exc.message}", extra={"path": str(request.url.path)})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(ConflictError)
async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """Handle ConflictError exceptions.

    Args:
        request: HTTP request
        exc: ConflictError exception

    Returns:
        409 JSON response
    """
    logger.warning(f"Conflict error: {exc.message}", extra={"path": str(request.url.path)})
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: HTTP request
        exc: Exception

    Returns:
        500 JSON response
    """
    logger.error(
        f"Unexpected error: {str(exc)}",
        exc_info=True,
        extra={"path": str(request.url.path)},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": settings.app_name}


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information.

    Returns:
        API information
    """
    return {
        "message": "URL List Management API",
        "version": "1.0.0",
        "docs": "/docs",
    }
