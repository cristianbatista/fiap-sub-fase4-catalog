import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from infrastructure.database.vehicle_document import VehicleDocument


async def init_db() -> None:
    mongodb_uri = os.environ["MONGODB_URI"]
    client = AsyncIOMotorClient(mongodb_uri)
    db_name = _extract_db_name(mongodb_uri)
    await init_beanie(database=client[db_name], document_models=[VehicleDocument])


def _extract_db_name(uri: str) -> str:
    if "/" not in uri.split("//", 1)[-1]:
        return "catalog"
    path = uri.split("/")[-1].split("?")[0]
    return path if path else "catalog"
