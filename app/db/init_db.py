from app.db.base import Base
from app.db.session import engine

# Import models here so SQLAlchemy registers them
from app.models.document import Document  


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)