from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Session

async def get_active_session_by_api_key(
    db: AsyncSession, api_key_id: int
) -> Optional[Session]:
    """
    Get an existing active session for an API key.
    
    Args:
        db: Database session
        api_key_id: API key ID
        
    Returns:
        Session object if found, None otherwise
    """
    result = await db.execute(
        select(Session)
        .where(Session.api_key_id == api_key_id, Session.is_active == True)
    )
    return result.scalars().first()

async def get_all_active_sessions(
    db: AsyncSession
) -> List[Session]:
    """
    Get all active sessions from the database.
    
    Args:
        db: Database session
        
    Returns:
        List of active Session objects
    """
    result = await db.execute(
        select(Session)
        .where(Session.is_active == True)
    )
    return result.scalars().all()

async def deactivate_existing_sessions(
    db: AsyncSession, api_key_id: int
) -> None:
    """
    Deactivate any existing active sessions for an API key.
    
    Args:
        db: Database session
        api_key_id: API key ID
    """
    await db.execute(
        update(Session)
        .where(Session.api_key_id == api_key_id, Session.is_active == True)
        .values(is_active=False)
    )
    await db.commit()

async def get_session_by_id(db: AsyncSession, session_id: str) -> Optional[Session]:
    """
    Get a session by ID.
    
    Args:
        db: Database session
        session_id: Session ID
        
    Returns:
        Session object if found, None otherwise
    """
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalars().first()

async def get_session(
    db: AsyncSession, session_id: str
) -> Optional[Session]:
    """
    Get a session by ID.
    
    Args:
        db: Database session
        session_id: Session ID
        
    Returns:
        Session object if found, None otherwise
    """
    return await get_session_by_id(db, session_id)

async def create_session(
    db: AsyncSession,
    session_id: str,
    api_key_id: Optional[int] = None,
    user_id: Optional[int] = None,
    model: str = None,
    session_type: str = "manual",
    expires_at: datetime = None,
) -> Session:
    """
    Create a new session.
    
    Args:
        db: Database session
        session_id: Session ID
        api_key_id: Optional API key ID
        user_id: Optional user ID
        model: Model name or blockchain ID
        session_type: Type of session (automated or manual)
        expires_at: Session expiration time
        
    Returns:
        Created Session object
    """
    if not expires_at:
        # Create a UTC datetime and convert to naive
        expires_at_with_tz = datetime.now(timezone.utc) + timedelta(hours=24)
        expires_at = expires_at_with_tz.replace(tzinfo=None)
    elif expires_at.tzinfo is not None:
        # If the provided expires_at has timezone info, convert to naive
        expires_at = expires_at.replace(tzinfo=None)
        
    session = Session(
        id=session_id,
        api_key_id=api_key_id,
        user_id=user_id,
        model=model,
        type=session_type,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session

async def mark_session_inactive(
    db: AsyncSession, session_id: str
) -> Optional[Session]:
    """
    Mark a session as inactive.
    
    Args:
        db: Database session
        session_id: Session ID
        
    Returns:
        Updated Session object if found, None otherwise
    """
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalars().first()
    
    if session:
        session.is_active = False
        await db.commit()
        await db.refresh(session)
    
    return session

async def get_session_by_api_key_id(
    db: AsyncSession, api_key_id: int
) -> Optional[Session]:
    """
    Get an active session associated with an API key ID.
    
    Args:
        db: Database session
        api_key_id: API key ID
        
    Returns:
        Session object if found, None otherwise
    """
    result = await db.execute(
        select(Session)
        .where(Session.api_key_id == api_key_id, Session.is_active == True)
    )
    return result.scalars().first()

async def delete_all_user_sessions(db: AsyncSession, user_id: int) -> int:
    """
    Delete all sessions for a user and return count of deleted sessions.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Count of deleted sessions
    """
    # Get count of sessions to delete
    count_result = await db.execute(
        select(Session).where(Session.user_id == user_id)
    )
    sessions = count_result.scalars().all()
    count = len(sessions)
    
    # Delete all sessions for the user
    await db.execute(
        delete(Session).where(Session.user_id == user_id)
    )
    await db.commit()
    
    return count 