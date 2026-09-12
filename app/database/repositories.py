from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.database.models import User, UsageLog
from datetime import datetime, timezone

async def get_or_create_user(session: AsyncSession, user_id: int, username: str, first_name: str) -> User:
    result = await session.execute(select(User).where(User.telegram_user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(telegram_user_id=user_id, username=username, first_name=first_name)
        session.add(user)
    else:
        user.username = username
        user.first_name = first_name
        user.last_active_at = datetime.now(timezone.utc)
    await session.commit()
    return user

async def increment_user_request(session: AsyncSession, user_id: int):
    stmt = update(User).where(User.telegram_user_id == user_id).values(
        request_count=User.request_count + 1,
        last_active_at=datetime.now(timezone.utc)
    )
    await session.execute(stmt)
    await session.commit()

async def log_usage(session: AsyncSession, user_id: int, feature: str, input_tokens: int = 0, output_tokens: int = 0):
    log = UsageLog(telegram_user_id=user_id, feature=feature, input_tokens=input_tokens, output_tokens=output_tokens)
    session.add(log)
    await session.commit()
