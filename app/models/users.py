from ..database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=text("now()") )
