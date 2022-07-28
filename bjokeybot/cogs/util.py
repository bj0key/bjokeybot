import random, re
from textwrap import shorten

from bjokeybot.logger import log
from discord.ext import commands


class UtilityCog(commands.Cog):

    pattern = re.compile(r"(\d*)d(\d+)\+?(\d*)", re.IGNORECASE)

    @commands.command(name="roll")
    async def diceroll(self, ctx: commands.Context, *args: str) -> None:
        "Rolls the specified dice"
        die = "".join(args)
        log.info("%s asked to roll %s", ctx.author.name, die)
        if (mtch := self.pattern.match(die)) is None:
            await ctx.reply("Invalid dice! Please specify in the format `2d6`")
            return

        count, size, bonus = mtch.groups()
        # print(count, size, bonus)
        count = int(count or 1)
        size = int(size)
        bonus = int(bonus or 0)

        if count > 5_000:
            await ctx.reply("Too many dice! Dice counts are limited to 5,000.")
            return
        if not 1 <= size <= 1_000_000:
            await ctx.reply("Dice size out of range! Dice sizes are limited to 1<=d<=1,000,000.")
            return

        rolls = [random.randint(1, size) for _ in range(count)]
        roll_sum = sum(rolls)

        if count > 50:
            rolls_txt = " + ".join(map(str, rolls[:49])) + " + ..." + str(rolls[50])
        else:
            rolls_txt = " + ".join(map(str, rolls))

        if bonus:
            rolls_txt = f"({rolls_txt}) + {bonus}"

        if count == 1:
            bonus_txt = "" if not bonus else f"+{bonus}"
            await ctx.reply(f"Your D{size}{bonus_txt} rolled a **{rolls[0] + bonus}**")
        else:
            await ctx.reply(
                f"Your D{size}s rolled {rolls_txt} = **{roll_sum + bonus}**"
            )
