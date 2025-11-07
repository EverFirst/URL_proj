"""Base repository interface with generic CRUD operations."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

# Type variable for domain entities
T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Base repository interface defining common CRUD operations.

    Generic type T represents the domain entity type.
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Retrieve entity by ID.

        Args:
            id: Entity identifier

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities.

        Returns:
            List of all entities (may be empty)
        """
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create new entity.

        Args:
            entity: Entity to create

        Returns:
            Created entity with generated ID
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity.

        Args:
            entity: Entity to update

        Returns:
            Updated entity
        """
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID.

        Args:
            id: Entity identifier

        Returns:
            True if deleted, False if not found
        """
        pass
