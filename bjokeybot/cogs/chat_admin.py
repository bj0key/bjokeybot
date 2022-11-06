from discord.ext import commands
from bjokeybot.logger import log


class ChatAdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="let", )
    async def voice_control(self, ctx: commands.Context, *names: str) -> None:
        log.info("%s used the speech command, with args %s", ctx.author.name, names)

        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("You're not an admin, shoo!")

        if ctx.author.voice is None:
            await ctx.reply("You can only silence people if you're in a voice channel!")

        if len(names) < 2 or names[-1] != "speak":
            await ctx.reply("Bad usage! Either let everyone speak, let noone speak, or let user1 user2 ... speak")
            return

        if names[0] == "me":
            async with ctx.typing():
                await ctx.author.edit(mute=False)
            await ctx.reply("You could've just unmuted yourself, you've got the permissions to... :rolling_eyes:")

        if names[0] in ("everyone", "everypony"):
            async with ctx.typing():
                for member in ctx.author.voice.channel.members:
                    await member.edit(mute=False)
            await ctx.reply("Fine, have your freedoms back...")

        elif names[0] == "nobody":
            async with ctx.typing():
                for member in ctx.author.voice.channel.members:
                    if member != ctx.author:
                        await member.edit(mute=True)
            await ctx.reply("SILENCEEE!!")

        else:
            async with ctx.typing():
                whitelist = set(names[:-1])
                for member in ctx.author.voice.channel.members:
                    if member != ctx.author and not any(
                            name in (member.name, member.nick, member.discriminator, "@" + member.discriminator) for
                            name in whitelist):
                        await member.edit(mute=True)
            await ctx.send("Be quiet, you rascals...")
