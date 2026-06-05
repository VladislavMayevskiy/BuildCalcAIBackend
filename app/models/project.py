from ..database import Base
from sqlalchemy import Column, Integer, String, text, JSON
from sqlalchemy.sql.sqltypes import TIMESTAMP



class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, nullable=False)
    materials = Column(JSON, nullable=False)
    subtotal_materials = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    assumptions = Column(JSON, nullable=False)
    warnings = Column(JSON, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
