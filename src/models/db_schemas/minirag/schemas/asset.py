from .minirag_base import SQL_alchemy_base
from .project import Project
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid


class Asset(SQL_alchemy_base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    type = Column(String, nullable=False)  # e.g., 'image', 'document'
    name = Column(String, nullable=False)
    size = Column(Integer, nullable=True)  # Size in bytes
    config = Column(JSONB, nullable=True)  # JSON configuration

    project_id = Column(
        Integer, ForeignKey("projects.id"), nullable=False
    )  # Foreign key to Project.id

    project = relationship("Project", back_populates="assets")

    __table_args__ = (
        Index("ix_asset_project_id", project_id),
        Index("ix_asset_type", type),
    )
