from discord.ext import commands


from discord.ext import commands

class DJ(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    
    def play() -> None:
        pass

def setup(bot):
    bot.add_cog(DJ(bot))