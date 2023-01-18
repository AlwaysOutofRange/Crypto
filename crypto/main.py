import os

from core.bot import CryptoBot

bot = CryptoBot()

if os.name != "nt":
    import uvloop

    uvloop.install()

if __name__ == "__main__":
    bot.run()
