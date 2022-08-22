import discord

from bjokeybot import logger
from bjokeybot.bot import BjokeyBot
from bjokeybot.constants import ACCESS_TOKEN
from bjokeybot.logger import log

logger.init_logger()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = BjokeyBot(command_prefix="bjokey, ", intents=intents)

bot.help_command = None


def main():
    log.info("Starting bot...")
    bot.run(ACCESS_TOKEN)


if __name__ == "__main__":
    main()
