import logging
from typing import Any

import dns.resolver
import motor.motor_asyncio
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

DB = None


class MongoDB:
    def __init__(self) -> None:
        pass

    def configure_default_resolver(self) -> None:
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = ["8.8.8.8"]

    @classmethod
    async def init(
        cls,
        url: str,
        database: str = "default",
        collection: str = "default",
        configure_default_resolver: bool = False,
    ) -> None:
        if configure_default_resolver:
            cls.configure_default_resolver(cls)

        cls._logger = logging.getLogger("crypto.database")
        cls._client = motor.motor_asyncio.AsyncIOMotorClient(
            url, serverSelectionTimeoutMS=300
        )
        cls._db = cls._client[database]
        cls._collection = cls._db[collection]

    def close(self) -> None:
        self._client.close()

    def get_client(self) -> MongoClient:
        return self._client

    def get_db(self) -> Database:
        return self._db

    def get_collection(self) -> Collection:
        return self._collection

    def set_collection(self, collection: str) -> None:
        if not self._collection == collection:
            self._collection = self._db[collection]

    def get_logger(self) -> logging.Logger:
        return self._logger

    async def test_connection(self) -> bool:
        try:
            server_info = await self._client.server_info()
            self._logger.info(server_info)
            return True
        except Exception as e:
            self._logger.exception(f"Failed to connect to database. {e}")
            return False

    async def insert_one(self, document: dict[Any, Any]) -> str:
        result = await self._collection.insert_one(document)

        self._logger.info("Inserted Document to Database")

        return repr(result.inserted_id)

    async def find_one(self, query: dict[Any, Any]) -> dict[Any, Any] | bool:
        result = await self._collection.find_one(query)

        if result:
            self._logger.info("Found requested document.")
            return result

        return False

    async def find_all(self, query: dict[Any, Any] = {}) -> list[Any]:
        return [doc async for doc in self._collection.find(query)]

    async def count(self, query: dict[Any, Any] = {}) -> int:
        return await self._collection.count_documents(query)

    async def delete_one(self, query: dict[Any, Any] = {}) -> int:
        result = await self._collection.delete_many(query)

        self._logger.info(f"Deleted Documents with the filter {query}")

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

        self._logger.info("Replaced Dokument.")

        return old, new

    async def update(
        self, query: dict[Any, Any], update: dict[Any, Any]
    ) -> tuple[int, Any]:
        result = await self._collection.update_one(query, {"$set": update})
        new_document = await self._collection.find_one(query)

        self._logger.info("Updated Dokument")

        return result.modified_count, new_document

    async def db_command(self, command: str) -> Any:
        return await self._db.command(command)
