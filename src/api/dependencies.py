"""Dependency injection setup for FastAPI routes.

This module provides factory functions for injecting repositories and services
into route handlers using FastAPI's Depends() mechanism.
"""
from typing import Generator
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db


# Database dependency (re-exported for convenience)
def get_database() -> Generator[Session, None, None]:
    """Get database session dependency.

    Yields:
        Database session

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_database)):
            ...
    """
    yield from get_db()


# Repository factories will be added here in future tasks
# Example:
# def get_list_repository(db: Session = Depends(get_database)) -> IListRepository:
#     return SQLAlchemyListRepository(db)

# Service factories will be added here in future tasks
# Example:
# def get_list_service(
#     list_repo: IListRepository = Depends(get_list_repository),
#     url_repo: IURLRepository = Depends(get_url_repository)
# ) -> ListService:
#     return ListService(list_repo, url_repo)
