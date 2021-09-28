from discord.ext import commands
from bot.helpers import helpers as h
import re
import youtube_dl
from discord import FFmpegOpusAudio
from configs.config import ROOT_PATH


# clase para administrar las colas de las canciones
class Cola:
    # TODO
    def __init__(self):
        self.cola: dict[str: list[str]] = {}

    def add_music(self, guild_id: str, music: str):
        self.cola[guild_id].append(music)


class DJ(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cola = Cola()
    
    async def join_on_channel(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("no estás es un canal de voz")
            return False
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
        return True

    @commands.command(name="play", aliases=["p"], description="play music")
    @commands.guild_only()
    async def play(self, ctx, *song: str):
        if not await self.join_on_channel(ctx):
            return

        if (song_url := song[0] if h.is_url(song) else h.url_by_name(song)) is None:
            await ctx.send("no se econtró tu chiste")
            return

        if len(music_info := self.get_ifo_music(song_url)) == 0:
            await ctx.send("zzzzz")
            return

        if (d := music_info['duration']) >= 422:
            await ctx.send("La canción dura mas de `7:00 min`, ***zzzzz***")
        else:
            url = music_info['formats'][0]['url']
            ffmpeg_options = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn",
                "executable": f"{ROOT_PATH}/configs/ffmpeg/bin/ffmpeg.exe"
            }
            voice_client = ctx.voice_client
            source = await FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
            voice_client.play(source, after=lambda e: print("done", e))
            voice_client.is_playing()
            print(url)
            await ctx.send(f"```json\n>>\"🎧 {music_info['title']} - {h.get_duration(d)}\" [{ctx.author}]```")

    def get_ifo_music(self, song_url) -> dict:
        ydl_options = {"format": "249"}
        try:
            with youtube_dl.YoutubeDL(ydl_options) as ydl:
                info_music = ydl.extract_info(song_url, download=False)
                return info_music
        except Exception as e:
            print(type(e).__name__)
        return {}

    @commands.command(name="disconnect", aliases=["d"], description="disconnect bot of voice channel")
    @commands.guild_only()
    async def disconnect(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command(name="stop", aliases=["s"], description="stop music")
    async def stop(self, ctx):
        ctx.voice_client.pause()

    @commands.command(name="resume", aliases=["r"], description="restart stop music")
    async def resume(self, ctx):
        ctx.voice_client.resume()

    def next(self, n=None):
        if n is None:
            pass
        else:
            print("mmmmmmmmmmmmmmmmmm")

    @commands.command(name="next", aliases=["n"], description="next music")
    @commands.guild_only()
    async def next_command(self, n):
        pass

    @commands.command(name="clear", aliases=["c"], description="clear queue")
    @commands.guild_only()
    async def clear(self) -> None:
        pass

    @commands.command(name="fav", aliases=["f"], description="add name or link fav music")
    @commands.guild_only()
    async def add_fav(self, ctx, song) -> None:
        # en teoría para usaurios premiun, o que verifique que tengan el rol de de vip
        pass


def setup(bot):
    bot.add_cog(DJ(bot))
