import os

from core.bot import CryptoBot


if __name__ == "__main__":
    bot = CryptoBot()

    if os.name != "nt":
        import uvloop

        uvloop.install()
    bot.run()
