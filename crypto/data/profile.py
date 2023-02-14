from typing import Any, Optional

import hikari
from hikari.embeds import Embed
from models.profilemodel import ProfileModel

from crypto.utils.db import MongoDB


class Profile:
    def __init__(self, user: hikari.Member, db: MongoDB) -> None:
        self.user = user
        self.db = db

        self.db.collection = "Profiles"

        self._id: int | None = None
        self._name: str | None = None
        self._money: int | None = None
        self._cryptocoins: int | None = None
        self._power: int | None = None
        self._miner: dict[str, int] | None = None

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def money(self) -> Optional[int]:
        return self._money

    @property
    def cryptocoins(self) -> Optional[int]:
        return self._cryptocoins

    @property
    def power(self) -> Optional[int]:
        return self._power

    @property
    def miner(self) -> Optional[dict[str, int]]:
        return self._miner

    async def create(self) -> Embed:
        result = await self.db.find_one({"_id": self.user.id})

        if result:
            embed = Embed(
                title="Error",
                description=(
                    "Sorry an error occurred it seems you already have a"
                    " profile."
                ),
                color=0x52000B,
            )

            return embed

        model = ProfileModel(self.user.id, self.user.username, 50, 0, 0, {})

        await self.db.insert_one(model.json)

        embed = Embed(
            title="Profile Created",
            description=(
                "Congratulations your profile has been successfully"
                " created.\n**Hint:** You can always view your stats or the"
                " stats of another user with the command `/profile search`."
            ),
            color=0x014001,
        )

        return embed

    async def get(self) -> dict[str, Any]:
        result = await self.db.find_one({"_id": self.user.id})

        if not isinstance(result, dict):
            return {"error": f"Data for user {str(self.user)} not found"}

        return {
            "id": result["_id"],
            "name": result["name"],
            "money": result["money"],
            "cryptocoins": result["cryptocoins"],
            "power": result["power"],
            "miners": result["miners"],
        }

    async def as_embed(self) -> Embed:
        result = await self.db.find_one({"_id": self.user.id})

        if not isinstance(result, dict):
            embed = Embed(
                title="Error",
                description=(
                    f"The requested profile for the user `{str(self.user)}`"
                    " was not Found.\n**Hint:** You can create a new profile"
                    " with `/profile create`."
                ),
                color=0x52000B,
            )
            return embed

        embed = Embed(
            title="Profile Found",
            description=(
                f"Here are the profile stats for the user `{str(self.user)}`."
            ),
            color=0x014001,
        )

        embed.add_field(name="ID", value=result["_id"], inline=True)
        embed.add_field(name="Name", value=result["name"], inline=True)
        embed.add_field(name="Money", value=result["money"], inline=True)
        embed.add_field(
            name="CryptoCoins", value=result["cryptocoins"], inline=True
        )
        embed.add_field(name="Power", value=result["power"], inline=True)
        embed.add_field(name="Miners", value=str(result["miner"]), inline=True)

        return embed

    async def update(self, data: dict[Any, Any]) -> bool:
        userdata = await self.db.find_one({"_id": self.user.id})

        if not isinstance(userdata, dict):
            return False

        await self.db.update(userdata, data)

        return True
