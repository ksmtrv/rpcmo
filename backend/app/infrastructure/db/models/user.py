from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, gen_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)
    email: Mapped[str | None] = mapped_column(nullable=True, index=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
