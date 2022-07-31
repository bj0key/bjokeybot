import ast
import random
import re

from discord.ext import commands

from bjokeybot.logger import log

EVAL_WHITELIST = (
    ast.Expression,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.BinOp,
    ast.UnaryOp,
    ast.operator,
    ast.unaryop,
    ast.cmpop,
    ast.Num,
)


class UtilityCog(commands.Cog):

    pattern = re.compile(r"(\d*)d(\d+)\+?(\d*)", re.IGNORECASE)

    @commands.command(name="roll")
    async def dice_roll(self, ctx: commands.Context, *, die: str) -> None:
        """Rolls the specified dice"""
        log.info("%s asked to roll %s", ctx.author.name, die)
        if (regex_match := self.pattern.fullmatch(die)) is None:
            await ctx.reply(
                "Invalid dice! Please specify in the format `[COUNT]d[SIZE]+[BONUS]`"
            )
            return

        count, size, bonus = regex_match.groups()
        # print(count, size, bonus)
        count = int(count or 1)
        size = int(size)
        bonus = int(bonus or 0)

        if count > 5_000:
            await ctx.reply("Too many dice! Dice counts are limited to 5,000.")
            return
        if not 1 <= size <= 1_000_000:
            await ctx.reply(
                "Dice size out of range! Dice sizes are limited to 1<=d<=1,000,000."
            )
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

    @commands.command(name="eval")
    async def math_eval(self, ctx: commands.Context, *, expr: str = "") -> None:
        """Safely*™ evaluates an arithmetic expression."""
        log.info('%s asked to evaluate "%s"', ctx.author.name, expr)

        tree = ast.parse(expr, mode="eval")
        valid = all(isinstance(node, EVAL_WHITELIST) for node in ast.walk(tree))
        if valid:
            result = eval(
                compile(tree, filename="", mode="eval"),
                {"__builtins__": None},
            )
            await ctx.reply(f"Evaluated {result}")
            return
        await ctx.reply("I'm not gonna evaluate that...")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        match ctx.command.name:
            case "eval":
                await ctx.reply("Invalid expression!")
            case "roll":
                await ctx.reply("Invalid dice!")
