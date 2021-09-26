import discord
from discord.ext import commands
from configs.config import TOKEN, DEFAULT_PREFIX
from bot.helpers import helpers as h

# Cogs
COGS = ["dj", "admin"]


class WaifuDJ(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, command_prefix=self.load_prefix)

    async def on_ready(self) -> None:
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(type=discord.ActivityType.listening, name="Bad bunny")
        )
        print("The bot is online")

    async def on_guild_join(self, guild) -> None:
        """
        Carga el prefijo por defecto relacionado al ID del server en
        donde el bot fue añadido
        """
        prefixes = h.read_prefixes()
        prefixes[str(guild.id)] = {"name_server": str(guild), "prefijo": DEFAULT_PREFIX}
        h.save_prefixes(prefixes)

        channels = []
        for channel in guild.channels:
            if isinstance(channel, discord.channel.TextChannel):
                if str(channel) == "general":
                    channels.insert(0, channel)
                else:
                    channels.append(channel)

        target_channel = None
        for channel in channels:
            if guild.me.permissions_in(channel).send_messages:
                target_channel = channel; break

        if target_channel is None:
            return

        # enviando un embed de intrucciones cuando el bot es agragado a un server
        # TODO: (refactorizar): crar una clase para trabajar los Embeds
        embed = discord.Embed(color=0xFE9AC9)
        embed.title = "Hola!!!"
        embed.description = "Hola soy \"WaifuDJ\" y mi prefijo por defecto es `?`"
        embed.url = "https://www.youtube.com/watch?v=ublf6qfpuuo"
        embed.set_thumbnail(url='https://i.pinimg.com/originals/6b/8b/a1/6b8ba1cbea0b91298960d4c00faca009.jpg')

        embed.add_field(
            name="Guía:",
            value=(
                "» `?setprefix <prefix>` => modificar prefijo (admin)\n"
                "» `?help` => comandos disponibles (all)\n"
            ),
            inline=False,
        )

        embed.set_footer(
            text="developed by n3mesis#1812",
            icon_url="https://i.pinimg.com/originals/77/d8/b7/77d8b7b9a34c9075153f2aa90c7531a1.png"
        )

        await target_channel.send(embed=embed)

    async def on_guild_remove(self, guild) -> None:
        prefixes = h.read_prefixes()
        if prefixes.pop(str(guild.id), None) is None:
            return
        else:
            h.save_prefixes(prefixes)

    def load_prefix(self, bot, message) -> None:
        """Cargar el prefijo relacionado a cada server"""
        prefixes = h.read_prefixes()
        if str(message.guild.id) in prefixes.keys():
            return prefixes[str(message.guild.id)]["prefijo"]
        else:
            return DEFAULT_PREFIX

    def load_cogs(self) -> None:
        """Cargar os COGS el cual son nustros comandos"""
        for cog in COGS:
            self.load_extension(f"bot.cogs.{cog}")

    def run(self) -> None:
        self.load_cogs()
        if TOKEN == "":
            print("no hay token papi!!!")
            exit()
        super().run(TOKEN)
