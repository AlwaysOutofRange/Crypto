import os
from dataclasses import dataclass

from dotenv import load_dotenv
from typing_extensions import Self


@dataclass
class Config:
    bot_token: str
    database_url: str
    database_db: str
    ...

    @classmethod
    def load(cls) -> Self:
        load_dotenv()

        if not os.getenv("TOKEN") and not os.getenv("MONGO_URL"):
            raise RuntimeError(
                "The keys 'TOKEN' and 'MONGO_URL' are not set in your .env"
                " file."
            )

        return Config(os.environ["TOKEN"], os.environ["MONGO_URL"], "Crypto")
