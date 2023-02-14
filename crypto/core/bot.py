import logging
import os

import hikari
import tanjun
import yuyo

from crypto.core.config import Config
from crypto.utils.db import MongoDB

from .client import Client


class CryptoBot(hikari.GatewayBot):
    def __init__(self) -> None:
        self.config = Config.load()
        self.logger = logging.getLogger("crypto.main")

        super().__init__(token=os.environ["TOKEN"], intents=hikari.Intents.ALL)
        self.component_client = yuyo.ComponentClient.from_gateway_bot(
            self, event_managed=False
        )
        self.db = MongoDB()

    def create_client(self) -> None:
        self.client = Client.from_gateway_bot(
            self,
            declare_global_commands=762272028622585866,
            mention_prefix=False,
        )
        (
            self.client.add_client_callback(
                tanjun.ClientCallbackNames.STARTING, self.component_client.open
            )
            .add_client_callback(
                tanjun.ClientCallbackNames.CLOSING, self.component_client.close
            )
            .add_client_callback(
                tanjun.ClientCallbackNames.STARTING, self.db.open
            )
            .add_client_callback(
                tanjun.ClientCallbackNames.CLOSING, self.db.close
            )
        )
        self.client.set_type_dependency(
            yuyo.ComponentClient, self.component_client
        )

        self.client.set_type_dependency(Config, self.config)
        self.client.set_type_dependency(MongoDB, self.db)

        self.client.load_modules()

    def run(self) -> None:
        self.create_client()

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_stopped)

        super().run()

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        self.logger.info("Bot Starting.")

    async def on_started(self, _: hikari.StartingEvent) -> None:
        self.logger.info("Bot is ready!")

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        self.logger.info("Bot is stopping.")

    async def on_stopped(self, _: hikari.StoppedEvent) -> None:
        self.logger.info("Bot has stopped!")
