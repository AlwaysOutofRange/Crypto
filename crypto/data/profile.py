import hikari
from hikari.embeds import Embed
from models.profilemodel import ProfileModel
from utils.db import MongoDB


class Profile:
    def __init__(self, user: hikari.Member, db: MongoDB) -> None:
        self.user = user
        self.db = db

    async def create_profile(self) -> Embed:
        result = await self.db.find_one({"_id": self.user.id})

        if result:
            embed = Embed(
                title="Error",
                description="Sorry an error occurred it seems you already have a profile.",
                color=0x52000B,
            )

            return embed

        model = ProfileModel(self.user.id, self.user.username, 50, 0, {})

        await self.db.insert_one(model.json)

        embed = Embed(
            title="Profile Created",
            description="Congratulations your profile has been successfully created.\n**Hint:** You can always view your stats or the stats of another user with the command `/profile search`.",
            color=0x014001,
        )

        return embed

    async def get_profile(self) -> Embed:
        result = await self.db.find_one({"_id": self.user.id})

        if not isinstance(result, dict):
            embed = Embed(
                title="Error",
                description=f"The requested profile for the user `{str(self.user)}` was not Found.\n**Hint:** You can create a new profile with `/profile create`.",
                color=0x52000B,
            )
            return embed

        embed = Embed(
            title="Profile Found",
            description=f"Here are the profile stats for the user `{str(self.user)}`.",
            color=0x014001,
        )

        embed.add_field(name="ID", value=result["_id"], inline=True)
        embed.add_field(name="Name", value=result["name"], inline=True)
        embed.add_field(name="Money", value=result["money"], inline=True)
        embed.add_field(name="CryptoCoins", value=result["cryptocoins"], inline=True)
        embed.add_field(name="Miners", value=str(result["miner"]), inline=True)

        return embed
