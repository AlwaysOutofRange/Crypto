from pathlib import Path
from typing import Any

import hikari
import tanjun
from typing_extensions import Self


class Client(tanjun.Client):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def load_modules(self: Self) -> Self:
        path = Path("./crypto/modules")

        for ext in path.glob(("**/") + "[!_]*.py"):
            super().load_modules(".".join([*ext.parts[:-1], ext.stem]))

        return self


@classmethod
def from_gateway_bot(
    cls,
    bot: hikari.GatewayBot,
    /,
    *,
    event_managed: bool = True,
    set_global_commands: hikari.Snowflake | bool = False,
) -> Client:
    contructor: Client = (
        cls(
            rest=bot.rest,
            cache=bot.cache,
            events=bot.event_manager,
            shards=bot,
            event_managed=event_managed,
            mention_prefix=False,
            set_global_commands=set_global_commands,
        )
        .set_human_only()
        .set_hikari_trait_injectors(bot)
    )

    return contructor
