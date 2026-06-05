from ..database import Base
from sqlalchemy import Column, Integer, ForeignKey, Float, String, text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class MaterialPrice(Base):
    __tablename__ = "material_prices"

    id = Column(Integer, primary_key=True, nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    source = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
