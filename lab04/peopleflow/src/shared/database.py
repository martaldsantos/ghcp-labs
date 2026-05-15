"""
Database configuration and session management.

We use SQLAlchemy with async sessions because the FastAPI stack is fully async.
Every query MUST be scoped to a tenant_id — our multi-tenancy model relies on
row-level isolation rather than separate schemas per tenant. This was chosen
for operational simplicity: one migration path, one connection pool, one backup
strategy. The trade-off is that every developer must remember to filter by
tenant_id, which is why we enforce it via the TenantQuery helper below.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# In production this comes from environment variables via pydantic-settings.
# For local dev, we default to a local PostgreSQL instance.
DATABASE_URL = "postgresql+asyncpg://peopleflow:peopleflow@localhost:5432/peopleflow"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models.

    Every model that represents tenant data MUST include a tenant_id column.
    Shared/global tables (e.g. platform config) are the exception and should
    be clearly documented.
    """
    pass


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session.

    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)

    The session is automatically committed on success and rolled back on error.
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


class TenantQuery:
    """Helper to ensure all queries are scoped to the correct tenant.

    Why this exists: In a multi-tenant system with row-level isolation, forgetting
    to filter by tenant_id is a data leak. This helper makes it harder to forget.

    Usage:
        query = TenantQuery(session, tenant_id)
        employees = await query.filter(Employee, Employee.department == "Engineering")
    """

    def __init__(self, session: AsyncSession, tenant_id: str):
        self.session = session
        self.tenant_id = tenant_id

    async def filter(self, model, *conditions):
        """Execute a SELECT with automatic tenant_id scoping."""
        from sqlalchemy import select

        stmt = select(model).where(
            model.tenant_id == self.tenant_id,
            *conditions,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, model, record_id: str):
        """Fetch a single record by ID, scoped to the tenant."""
        from sqlalchemy import select

        stmt = select(model).where(
            model.tenant_id == self.tenant_id,
            model.id == record_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
