from ..database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, text, JSON
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True,nullable=False)
    input_data = Column(JSON, nullable = False)
    result_data = Column(JSON, nullable = False )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_project_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    calculation_type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable= False, server_default=text("now()"))