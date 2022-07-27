import asyncio
import os

import discord
from discord.ext import commands

from bjokeybot import cogs, logger
from bjokeybot.constants import ACCESS_TOKEN
from bjokeybot.logger import log

os.chdir(os.path.dirname(__file__))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="bjokey, ", intents=intents)

bot.help_command = None

logger.init_logger()


async def setup():
    await bot.add_cog(cogs.FunCog())
    await bot.add_cog(cogs.StatsCog())
    await bot.add_cog(cogs.TTSCog())


def main():
    log.info(f"Starting bot...")
    bot.run(ACCESS_TOKEN)


if __name__ == "__main__":
    asyncio.run(setup())
    main()
