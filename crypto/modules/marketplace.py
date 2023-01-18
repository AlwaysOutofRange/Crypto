import datetime
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

import hikari
import tanjun
import yuyo
from utils.db import MongoDB

component = tanjun.Component()
marketplace_group = component.with_slash_command(
    tanjun.slash_command_group("marketplace", "Marketplace")
)


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
            db.set_collection("Marketplace")
            data = await db.find_all()

            await ctx.set_choices(
                {miner["name"]: miner["name"] for miner, _ in zip(data, range(25))}
            )

        except tanjun.CommandError:
            await ctx.set_choices()

    return _autocomplete


@marketplace_group.with_command
@tanjun.as_slash_command("all", "Show all available miner")
async def marketplace_all(
    ctx: tanjun.abc.Context,
    db: MongoDB = tanjun.injected(type=MongoDB),
    component_client: yuyo.ComponentClient = tanjun.injected(type=yuyo.ComponentClient),
) -> None:
    if ctx.member is None or not db:
        return

    db.set_collection("Marketplace")
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
                name="Description", value=f"`{miner['description']}`", inline=False
            )
            .add_field(name="Price", value=f"`{miner['price']}$`", inline=True)
            .add_field(
                name="Hashrate", value=f"`{miner['hashrate']} TH/s`", inline=True
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
            yuyo.pagination.LEFT_DOUBLE_TRIANGLE,
            yuyo.pagination.LEFT_TRIANGLE,
            yuyo.pagination.STOP_SQUARE,
            yuyo.pagination.RIGHT_TRIANGLE,
            yuyo.pagination.RIGHT_DOUBLE_TRIANGLE,
        ),
    )

    if first_respone := await paginator.get_next_entry():
        _, embed = first_respone
        message = await ctx.respond(
            component=paginator, embed=embed, ensure_result=True
        )
        component_client.set_executor(message, paginator)
        return

    await ctx.respond("Miner not found in Database!")


@marketplace_group.with_command
@tanjun.with_str_slash_option(
    "miner", "Select a miner", autocomplete=make_autocomplete()
)
@tanjun.as_slash_command("find", "Buy a specific miner")
async def marketplace_find(
    ctx: tanjun.abc.Context, miner: str, db: MongoDB = tanjun.injected(type=MongoDB)
) -> None:
    db.set_collection("Marketplace")

    data = await db.find_one({"name": miner})

    if not isinstance(data, dict):
        await ctx.respond(
            embed=hikari.Embed(
                title="Error",
                description="The requested miner was not found in the database",
                color=0x52000B,
            )
        )
        return

    embed = hikari.Embed(
        title="Marketplace",
        description=f"Here are the requested information from the miner `{data['name']}`",
        color=0x280134,
        timestamp=datetime.datetime.now().astimezone(),
    )
    embed.add_field(name="Name", value=f"`{data['name']}`", inline=True)
    embed.add_field(name="Description", value=f"`{data['description']}`", inline=False)
    embed.add_field(name="Price", value=f"`{data['price']}$`", inline=True)
    embed.add_field(name="Hashrate", value=f"`{data['hashrate']} TH/s`", inline=True)
    embed.add_field(
        name="Power Consumption",
        value=f"`{data['power_consumption']} watts`",
        inline=True,
    )

    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Any) -> None:
    client.add_component(component.copy())
