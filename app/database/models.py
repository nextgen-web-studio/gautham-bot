from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    request_count = Column(Integer, default=0)

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, index=True)
    feature = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
