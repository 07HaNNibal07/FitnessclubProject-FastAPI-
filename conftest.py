import pytest_asyncio
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from app.core import Base,db_helper,rate_limit
from httpx import AsyncClient, ASGITransport
from redis.asyncio import Redis
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = "postgresql+asyncpg://test:test123@test_db:5432/testfitnessclub"
TEST_REDIS_URL = Redis(host="test_redis", port=6379, decode_responses=True)

test_session_engine = create_async_engine(TEST_DATABASE_URL,poolclass = NullPool)

TestSessionMaker = async_sessionmaker(test_session_engine,expire_on_commit=False)

async def test_current_session():
    async with TestSessionMaker() as session:
        yield session

async def override_invalidate_trainers_cache():
    return None

async def override_rate_limit():
    return None

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_test_db():
    async with test_session_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_session_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    await test_session_engine.dispose()

@pytest_asyncio.fixture
async def user(monkeypatch):
    monkeypatch.setattr(
        "app.routers.trainers.invalidate_trainers_cache",
        override_invalidate_trainers_cache
    )
     
    app.dependency_overrides[db_helper.current_session] = test_current_session
    app.dependency_overrides[rate_limit] = override_rate_limit

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()