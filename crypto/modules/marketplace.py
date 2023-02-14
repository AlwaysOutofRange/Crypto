import datetime

import hikari
import tanjun
import yuyo
from data.profile import Profile
from hikari import ButtonStyle, Emoji

from crypto.utils.db import MongoDB

marketplace_group = tanjun.slash_command_group("marketplace", "Marketplace")


async def buy_button_callback(
    yuyoContext: yuyo.ComponentContext,
    db: MongoDB,
) -> None:
    db.collection = "Marketplace"

    miner_name = (
        yuyoContext.interaction.message.embeds[0]
        .fields[0]
        .value.replace("`", "")
    )

    if not yuyoContext.interaction.member:
        return

    miner_data = await db.find_one({"name": miner_name})

    if not isinstance(miner_data, dict):
        await yuyoContext.respond("Error")
        return

    profile = Profile(yuyoContext.interaction.member, db)
    profile_dict = await profile.get()

    miners = {
        miner_data["name"]: profile_dict["miners"][miner_data["name"]] + 1
    }

    success = await profile.update(profile_dict | miners)

    if success:
        await yuyoContext.respond(embed=await profile.as_embed())


async def sell_button_callback(
    yuyoContext: yuyo.ComponentContext,
    db: MongoDB = tanjun.injected(type=MongoDB),
) -> None:
    await yuyoContext.respond("Pressed Sell button")


def make_autocomplete() -> tanjun.abc.AutocompleteCallbackSig:
    async def _autocomplete(
        ctx: tanjun.abc.AutocompleteContext,
        value: str,
        db: MongoDB = tanjun.injected(type=MongoDB),
    ) -> None:
        if not value:
            await ctx.set_choices()
            return

        try:
            db.collection = "Marketplace"
            data = await db.find_all()

            await ctx.set_choices(
                {
                    miner["name"]: miner["name"]
                    for miner, _ in zip(data, range(25))
                }
            )

        except tanjun.CommandError:
            await ctx.set_choices()

    return _autocomplete


@marketplace_group.add_command
@tanjun.as_slash_command("all", "Show all available miner")
async def marketplace_all(
    ctx: tanjun.abc.Context,
    db: MongoDB = tanjun.injected(type=MongoDB),
    component_client: yuyo.ComponentClient = tanjun.injected(
        type=yuyo.ComponentClient
    ),
) -> None:
    if not db:
        return

    db.collection = "Marketplace"
    data = await db.find_all()
    data_len = len(data)

    iterator = (
        (
            hikari.UNDEFINED,
            hikari.Embed(
                color=0x280134,
                title="Marketplace",
                description="Select a miner you want to buy.",
                timestamp=datetime.datetime.now().astimezone(),
            )
            .add_field(name="Name", value=f"`{miner['name']}`", inline=True)
            .add_field(
                name="Description",
                value=f"`{miner['description']}`",
                inline=False,
            )
            .add_field(name="Price", value=f"`{miner['price']}$`", inline=True)
            .add_field(
                name="Hashrate",
                value=f"`{miner['hashrate']} TH/s`",
                inline=True,
            )
            .add_field(
                name="Power Consumption",
                value=f"`{miner['power_consumption']} watts`",
                inline=True,
            )
            .set_footer(f"Page: {i + 1}/{data_len}"),
        )
        for i, miner in enumerate(data)
    )

    paginator = yuyo.ComponentPaginator(
        iterator,
        authors=(ctx.author,),
        timeout=datetime.timedelta(minutes=3),
        triggers=(
            yuyo.pagination.LEFT_TRIANGLE,
            yuyo.pagination.STOP_SQUARE,
            yuyo.pagination.RIGHT_TRIANGLE,
        ),
    )

    executor = (
        yuyo.MultiComponentExecutor()
        .add_executor(paginator)
        .add_builder(paginator)
        .add_action_row()
        .add_button(ButtonStyle.PRIMARY, buy_button_callback)
        .set_emoji(Emoji.parse("<:shoppingcart:1066059480959299744>"))
        .set_label("Buy x1")
        .add_to_container()
        .add_button(ButtonStyle.DANGER, sell_button_callback)
        .set_emoji(Emoji.parse("<:cash:1066064579223879820>"))
        .set_label("Sell x1")
        .add_to_container()
        .add_to_parent()
    )

    executor._timeout = datetime.timedelta(minutes=3)

    if first_respone := await paginator.get_next_entry():
        _, embed = first_respone
        message = await ctx.respond(
            components=executor.builders, embed=embed, ensure_result=True
        )
        component_client.set_executor(message, executor)
        return

    await ctx.respond("Miner not found in Database!")


@marketplace_group.add_command
@tanjun.with_str_slash_option(
    "miner", "Select a miner", autocomplete=make_autocomplete()
)
@tanjun.as_slash_command("find", "Buy a specific miner")
async def marketplace_find(
    ctx: tanjun.abc.Context,
    miner: str,
    db: MongoDB = tanjun.injected(type=MongoDB),
) -> None:
    db.collection = "Marketplace"

    data = await db.find_one({"name": miner})

    if not isinstance(data, dict):
        await ctx.respond(
            embed=hikari.Embed(
                title="Error",
                description=(
                    "The requested miner was not found in the database"
                ),
                color=0x52000B,
            )
        )
        return

    embed = hikari.Embed(
        title="Marketplace",
        description=(
            "Here are the requested information from the miner"
            f" `{data['name']}`"
        ),
        color=0x280134,
        timestamp=datetime.datetime.now().astimezone(),
    )
    embed.add_field(name="Name", value=f"`{data['name']}`", inline=True)
    embed.add_field(
        name="Description", value=f"`{data['description']}`", inline=False
    )
    embed.add_field(name="Price", value=f"`{data['price']}$`", inline=True)
    embed.add_field(
        name="Hashrate", value=f"`{data['hashrate']} TH/s`", inline=True
    )
    embed.add_field(
        name="Power Consumption",
        value=f"`{data['power_consumption']} watts`",
        inline=True,
    )

    await ctx.respond(embed=embed)


component = tanjun.Component(name=__name__).load_from_scope().make_loader()
