from discord.ext import commands

class DJ(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="play", aliases=["p"], description="play musics")
    async def play(self) -> None:
        pass


def setup(bot):
    bot.add_cog(DJ(bot))