import random
import discord
import matplotlib.pyplot as plt

from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="bjokey, ", intents=intents)

bjokey_image = discord.File("bjokey.png")
with open("token") as file:
    __token = file.read()

bot.help_command = None


@bot.command(name="bjokey")
async def bjokey(ctx: commands.Context):
    if random.random() < 0.95:
        await ctx.reply("bjokey")
    else:
        await ctx.reply("rare bjokey", file=bjokey_image)


@bot.command(name="femham")
async def femham(ctx: commands.Context):
    if ctx.message.author.id == 66183829148151808:
        await ctx.reply("Why are you trying to use the command, cris")
    else:
        await ctx.reply(f"stop femming cris{'tine'*random.randint(0,1)}")
        bot.fetch_user()


@bot.command(name="genders")
async def genders(ctx: commands.Context):
    plt.style.use("dark_background")
    plt.figure(figsize=(16, 8))
    plt.grid(axis="y", alpha=0.25)

    genders = [
        (r.name, len(r.members), r.color)
        for r in ctx.guild.roles
        if "/" in r.name or r.name in ("Norway", "Just use my name", "All Pronouns")
    ]

    for gender, count, colour in sorted(genders, key=lambda x: x[1]):
        plt.bar(
            gender, count, color=(colour.r / 255, colour.g / 255, colour.b / 255, 1),
            zorder=10
        )

    plt.yticks(range(0, max(v[1] for v in genders) + 1))
    plt.savefig("figure.png")

    diagram = discord.File("figure.png")

    await ctx.reply(file=diagram)


print(f"Starting bot...")
bot.run(__token)
