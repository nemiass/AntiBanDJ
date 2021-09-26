from discord.ext import commands
from bot.helpers import helpers as h


class Admin(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="setprefix", aliases=["sp"], description="cambiar prefijo")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix) -> None:
        if len(prefix) == 1:
            prefixes = h.read_prefixes()
            prefixes[str(ctx.guild.id)]["prefijo"] = prefix
            h.save_prefixes(prefixes)


def setup(bot):
    bot.add_cog(Admin(bot))
