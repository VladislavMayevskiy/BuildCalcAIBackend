from ..database import Base
from sqlalchemy import Column, Integer, String, Float, text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    unit = Column(String, nullable=False)
    default_price = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    source = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
