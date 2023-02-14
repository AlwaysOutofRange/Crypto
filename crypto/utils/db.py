import logging
from typing import Any

import motor.motor_asyncio
import tanjun
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from crypto.core.config import Config


class MongoDB:
    def __init__(self) -> None:
        self._logger: Any = None
        self._client: Any = None
        self._db: Any = None
        self._collection: Any = None

    async def open(
        self,
        config: Config = tanjun.injected(type=Config),
    ) -> None:
        self._logger = logging.getLogger("crypto.database")
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            config.database_url, serverSelectionTimeoutMS=300
        )
        self._db = self._client[config.database_db]
        self._collection = self._db["Profiles"]

    def close(self) -> None:
        self._client.close()

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def db(self) -> Database:
        return self._db

    @db.setter
    def db(self, value: str) -> None:
        self._db = self.client[value]

    @property
    def collection(self) -> Collection:
        return self._collection

    @collection.setter
    def collection(self, value: str) -> None:
        self._collection = self.db[value]

    @property
    def logger(self):
        return self._logger

    async def test_connection(self) -> bool:
        try:
            server_info = await self._client.server_info()
            self.logger.info(server_info)
            return True
        except Exception as e:
            self.logger.exception(f"Failed to connect to database. {e}")
            return False

    async def insert_one(self, document: dict[Any, Any]) -> str:
        result = await self._collection.insert_one(document)

        return repr(result.inserted_id)

    async def find_one(self, query: dict[Any, Any]) -> dict[Any, Any] | bool:
        result = await self._collection.find_one(query)

        if result:
            return result

        return False

    async def find_all(self, query: dict[Any, Any] = {}) -> list[Any]:
        return [doc async for doc in self._collection.find(query)]

    async def count(self, query: dict[Any, Any] = {}) -> int:
        return await self._collection.count_documents(query)

    async def delete_one(self, query: dict[Any, Any] = {}) -> int:
        result = await self._collection.delete_many(query)

        return result.deleted_count

    async def replace(
        self, query: dict[Any, Any], new_data: dict[Any, Any]
    ) -> tuple[Any, Any]:
        old = await self._collection.find_one(query)
        if old is None:
            return (), ()

        _id = old["_id"]
        await self._collection.replace_one({"_id": _id}, new_data)
        new = await self._collection.find_one({"_id": _id})

        return old, new

    async def update(
        self, query: dict[Any, Any], update: dict[Any, Any]
    ) -> tuple[int, Any]:
        result = await self._collection.update_one(query, {"$set": update})
        new_document = await self._collection.find_one(query)

        return result.modified_count, new_document

    async def db_command(self, command: str) -> Any:
        return await self._db.command(command)
