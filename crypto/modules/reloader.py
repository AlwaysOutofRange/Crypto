import tanjun

reloader_group = tanjun.slash_command_group("module", "Module reloader")


def make_autocomplete() -> tanjun.abc.AutocompleteSig:
    async def _autocomplete(
        ctx: tanjun.abc.AutocompleteContext,
        value: str,
    ) -> None:
        if not value:
            await ctx.set_choices()
            return

        try:
            await ctx.set_choices(
                {
                    module.name: module.name
                    for module, _ in zip(ctx.client.components, range(25))
                }
            )
        except tanjun.CommandError:
            await ctx.set_choices()

    return _autocomplete


@reloader_group.add_command
@tanjun.with_str_slash_option(
    "name", "The module to target.", autocomplete=make_autocomplete()
)
@tanjun.as_slash_command("reload", "Reloads a module.")
async def reload_module(
    ctx: tanjun.abc.SlashContext,
    name: str,
    client: tanjun.Client = tanjun.injected(type=tanjun.Client),
) -> None:
    if ctx.author.id != 346952827970781185:
        await ctx.respond("You can't use this command!")
        return

    try:
        client.reload_modules(name)
    except ValueError:
        client.load_modules(name)

    await ctx.respond(f"⚙️♻️ Reloaded `{name}`")


@reloader_group.add_command
@tanjun.with_str_slash_option(
    "name", "The module to target.", autocomplete=make_autocomplete()
)
@tanjun.as_slash_command("unload", "Removes a module.")
async def unload_module(
    ctx: tanjun.abc.SlashContext,
    name: str,
    client: tanjun.Client = tanjun.injected(type=tanjun.Client),
) -> None:
    if ctx.author.id != 346952827970781185:
        await ctx.respond("You can't use this command!")
        return

    try:
        client.unload_modules(name)
    except ValueError:
        await ctx.respond(f"❗ Couldn't unload `{name}`")
        return

    await ctx.respond(f"⚙️📤 Unloaded `{name}`")


@reloader_group.add_command
@tanjun.with_str_slash_option(
    "name", "The module to target.", autocomplete=make_autocomplete()
)
@tanjun.as_slash_command("load", "Loads a module.")
async def load_module(
    ctx: tanjun.abc.SlashContext,
    name: str,
    client: tanjun.Client = tanjun.injected(type=tanjun.Client),
) -> None:
    if ctx.author.id != 346952827970781185:
        await ctx.respond("You can't use this command!")
        return

    try:
        client.load_modules(name)
    except ValueError:
        await ctx.respond(f"❗ Couldn't load `{name}`")
        return

    await ctx.respond(f"⚙️  Loaded `{name}`")


component = tanjun.Component(name=__name__).load_from_scope().make_loader()
