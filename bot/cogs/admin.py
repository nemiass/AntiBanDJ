from discord.ext import commands
from bot.helpers import helpers as h


class Admin(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="setprefix", aliases=["sp"], description="cambiar prefijo")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set_prefix(self, ctx, prefix) -> None:
        prefixes = h.read_prefixes()
        prefixes[str(ctx.guild.id)]["prefijo"] = prefix
        h.save_prefixes(prefixes)
        await ctx.send(f"```json\n{prefixes[str(ctx.guild.id)]}```")


def setup(bot):
    bot.add_cog(Admin(bot))
