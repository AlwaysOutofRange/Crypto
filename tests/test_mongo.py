# import os
# import pytest
#
# from dotenv import load_dotenv
#
# from crypto.utils.db import MongoDB
#
# load_dotenv()
#
# if not os.getenv("MONGO_URL"):
#     raise RuntimeError("MONGO_URL not set in .env file")
#
# db = MongoDB()
# test_data = {"_id": 346952827970781185, "count": 1, "name": "test"}
#
# class TestMongo:
#     pytestmark = pytest.mark.asyncio
#
#     async def init_connection(self) -> None:
#         await db.init(os.environ["MONGO_URL"], "Crypto", "Profiles")
#
#         assert True
#
#     async def test_conntection(self) -> None:
#         assert await db.test_connection()
#
#     async def test_insert_one(self) -> None:
#         result = await db.insert_one(test_data)
#
#         assert result == repr(test_data["_id"])
#
#     async def test_find_one(self) -> None:
#         result = await db.find_one(test_data)
#
#         assert isinstance(result, dict)
#
#     async def test_find_all(self) -> None:
#         result = await db.find_all(test_data)
#
#         assert len(result) > 0
#
#     async def test_count(self) -> None:
#         result = await db.count(test_data)
#
#         assert result > 0
#
#     async def test_delete_one(self) -> None:
#         result = await db.delete_one(test_data)
#
#         assert result > 0
#
#     async def test_replace(self) -> None:
#         await db.insert_one(test_data)
#
#         new_data = {"name": "outofrange", "count": "17"}
#
#         old, new = await db.replace(test_data, new_data)
#
#         assert old != new
#
#         await db.delete_one(new_data)
#
#     async def test_update(self) -> None:
#         await db.insert_one(test_data)
#
#         update_count, _ = await db.update(test_data, {"name": "outofrange"})
#
#         assert update_count > 0
#
#         await db.delete_one({"name": "outofrange"})
