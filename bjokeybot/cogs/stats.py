from io import BytesIO

from bjokeybot.logger import log
from discord import File
from discord.ext import commands
from matplotlib import pyplot as plt


class StatsCog(commands.Cog):
    @commands.command(name="genders")
    async def genders(self, ctx: commands.Context) -> None:
        log.info("%s ran genders.", ctx.author.name)
        plt.style.use("dark_background")
        plt.figure(figsize=(16, 8))
        plt.grid(axis="y", alpha=0.25)

        genders = [
            (r.name, len(r.members), r.color)
            for r in ctx.guild.roles
            if "/" in r.name or r.name in ("Norway", "Just use my name", "All Pronouns")
        ]

        log.debug("Current Data: %s", genders)

        for gender, count, colour in sorted(genders, key=lambda x: x[1]):
            plt.bar(
                gender,
                count,
                color=(colour.r / 255, colour.g / 255, colour.b / 255, 1),
                zorder=10,
            )

        plt.yticks(range(0, max(v[1] for v in genders) + 1))
        with BytesIO() as f:
            plt.savefig(f, format="png")
            f.seek(0)
            await ctx.reply(file=File(f, filename="genders.png"))
