from ..database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, text, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    length = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    room_type = Column(String, nullable=False)
    doors_area = Column(Float, nullable=False)
    windows_area = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=text("now()") )

