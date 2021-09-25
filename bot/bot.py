import discord
from discord.ext import commands
from configs.config import TOKEN, DEFAULT_PREFIX
from helpers import helpers as h


COGS = {
    "dj"
}

class Waifu_DJ(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, command_prefix=self.load_prefix)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            status=discord.Status.idle,
            activity=discord.Game("las escodidas")
        )
        print("The bot is online")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Carga el prefijo por defecto relacionado al ID del server en
        donde el bot fue añadido
        """
        prefixes = h.read_prefixes()
        prefixes[str(guild.id)] = {"prefijo": DEFAULT_PREFIX}
        h.save_prefixes(prefixes)

    def load_prefix(bot, message) -> None:
        """Cargar el prefijo relacionado a cada server"""
        return h.read_prefixes()[str(message.guild.id)]["prefijo"]

    def load_cogs(self) -> None:
        """Cargar os COGS el cual son nustros comandos"""
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")
    
    def run(self) -> None:
        self.load_cogs()
        super().run(TOKEN)
