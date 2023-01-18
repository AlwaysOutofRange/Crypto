from typing import Any

import hikari
import tanjun
from utils.db import MongoDB

from crypto.data.profile import Profile

component = tanjun.Component()
profile_group = component.with_slash_command(
    tanjun.slash_command_group("profile", "Profile managment")
)


@profile_group.with_command
@tanjun.with_member_slash_option("member", "User to show the stats from", default=None)
@tanjun.as_slash_command("search", "Show your stats or from another user")
async def profile_search(
    ctx: tanjun.abc.Context,
    member: hikari.Member,
    db: MongoDB = tanjun.injected(type=MongoDB),
) -> None:
    db.set_collection("Profiles")

    if ctx.member is None or not db:
        return

    if member is None:
        profile = Profile(ctx.member, db)
    else:
        profile = Profile(member, db)

    await ctx.respond(embed=await profile.get_profile())


@profile_group.with_command
@tanjun.as_slash_command("create", "Create a new profile")
async def profile_create(
    ctx: tanjun.abc.Context, db: MongoDB = tanjun.injected(type=MongoDB)
) -> None:
    db.set_collection("Profiles")

    if ctx.member is None or not db:
        return

    profile = Profile(ctx.member, db)

    await ctx.respond(embed=await profile.create_profile())


@tanjun.as_loader
def load_components(client: Any) -> None:
    client.add_component(component.copy())
