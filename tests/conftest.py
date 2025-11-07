"""Pytest fixtures for testing."""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from src.infrastructure.models import Base
from src.infrastructure.database import get_db
from src.main import app


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Create test database session with in-memory SQLite.

    Yields:
        Test database session

    Usage:
        def test_repository(test_db):
            repo = SQLAlchemyListRepository(test_db)
            ...
    """
    # Create test engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db: Session) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with test database.

    Args:
        test_db: Test database session fixture

    Yields:
        FastAPI test client

    Usage:
        def test_endpoint(test_client):
            response = test_client.post("/lists", json={"title": "Test"})
            assert response.status_code == 201
    """

    # Override get_db dependency to use test database
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as client:
        yield client

    # Clear dependency overrides
    app.dependency_overrides.clear()


# Mock repository fixtures will be added in future tasks
# Example:
# @pytest.fixture
# def mock_list_repository():
#     return Mock(spec=IListRepository)
