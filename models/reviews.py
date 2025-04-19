from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String
from backend.db import Base


class Review(Base):
    """Модель отзыва."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    comment = Column(String, nullable=True)
    comment_date = Column(DateTime, default=datetime.now())
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)
