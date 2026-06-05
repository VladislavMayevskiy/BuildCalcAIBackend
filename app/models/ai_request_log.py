from ..database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, text, Text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    calculation_id = Column(Integer, ForeignKey("calculations.id", ondelete="CASCADE"), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()") )

