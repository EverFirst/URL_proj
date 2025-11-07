"""SQLAlchemy ORM models for URL List Management API."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship, declarative_base
from typing import List

Base = declarative_base()


class URLListModel(Base):
    """URLList ORM model - represents a collection of URLs."""

    __tablename__ = "url_lists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(50), unique=True, nullable=True, index=True)
    status = Column(
        SQLEnum("draft", "published", name="status_enum"),
        nullable=False,
        default="draft",
        index=True,
    )
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    urls: List["URLItemModel"] = relationship(
        "URLItemModel",
        back_populates="list",
        cascade="all, delete-orphan",
        order_by="URLItemModel.created_at",
    )

    def __repr__(self) -> str:
        return f"<URLListModel(id={self.id}, title='{self.title}', status='{self.status}')>"


class URLItemModel(Base):
    """URLItem ORM model - represents a single URL entry in a list."""

    __tablename__ = "url_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey("url_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)

    # Relationships
    list: "URLListModel" = relationship("URLListModel", back_populates="urls")

    def __repr__(self) -> str:
        return f"<URLItemModel(id={self.id}, url='{self.url}', list_id={self.list_id})>"
