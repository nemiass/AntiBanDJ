from discord.ext import commands
from bot.helpers import helpers as h
import youtube_dl
from discord import FFmpegOpusAudio, HTTPException
from configs.config import ROOT_PATH
from asyncio import Queue, Event, get_event_loop
from async_timeout import timeout
from functools import partial


FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
    "executable": f"{ROOT_PATH}/configs/ffmpeg/bin/ffmpeg.exe"
}


class Player:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        # la clase cog
        self.cog_dj = ctx.cog
        # para guardar el mensaje
        self.np = None

        self.queue = Queue()
        # https://docs.python.org/es/3.9/library/asyncio-sync.html , documentacion de asyncio.Event
        self.evet = Event()

        ctx.bot.loop.create_task(self.event_player())

    async def event_player(self):
        # is_closed() bool: Indica si la conexión websocket está cerrada
        while not self.bot.is_closed():
            self.evet.clear()  # colocando a event en False
            try:
                async with timeout(300):
                    music_source = await self.queue.get()
            except TimeoutError:
                if self in self.cog_dj.music_players.values():
                    return self.destroy(self.guild)

            if not isinstance(music_source["s"], FFmpegOpusAudio):
                song_url = music_source["l"]
                autor = music_source["a"]
                music_info = await self.get_ifo_music(song_url, self.bot.loop)
                if len(music_info) == 0:
                    await self.channel.send(f"error al buscar {song_url}", delete_after=5)
                    continue
                url = music_info['formats'][0]['url']
                title = music_info['title']
                duration = h.get_duration(music_info["duration"])
                source = await FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                music_source = {"s": source, "t": title, "d": duration, "a": autor}

            self.guild.voice_client.play(music_source["s"],
                                         after=lambda _: self.bot.loop.call_soon_threadsafe(self.evet.set))
            self.np = await self.channel.send(f"```json\n>>\"🎧 {music_source['t']} - " 
                                              f"{music_source['d']}\" [{music_source['a']}]```")
            await self.evet.wait()

            # limpia el source de audio de ffmpeg
            music_source["s"].cleanup()

            try:
                # borra el mensaje de play antiguo
                await self.np.delete()
            except HTTPException:
                pass

    async def get_ifo_music(self, song_url, loop):
        loop = loop or get_event_loop()
        ydl_options = {"format": "249"}
        try:
            with youtube_dl.YoutubeDL(ydl_options) as ydl:
                to_run = partial(ydl.extract_info, url=song_url, download=False)
                info_music = await loop.run_in_executor(None, to_run)
                return info_music
        except Exception as e:
            print(type(e).__name__)
        return {}

    async def destroy(self, guild):
        # crear una tarea para desconectar y destruir el player
        return self.bot.loop.create_task(self.cog_dj.cleanup(guild))


class DJ(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.music_players = {}
    
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

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()

            for source in self.music_players[guild.id].queue._queue:
                if isinstance(source, FFmpegOpusAudio):
                    source.cleanup()
            self.music_players[guild.id].queue._queue.clear()

            del self.music_players[guild.id]

        except AttributeError:
            pass

        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.music_players[ctx.guild.id]
        except KeyError:
            player = Player(ctx)
            self.music_players[ctx.guild.id] = player
        return player

    @commands.command(name="play", aliases=["p"], description="play music")
    @commands.guild_only()
    async def play(self, ctx, *song: str):
        if not await self.join_on_channel(ctx):
            return

        if (song_url := song[0] if h.is_url(song) else h.url_by_name(song)) is None:
            await ctx.send("no se econtró tu chiste", delete_after=5)
            return
        player = self.get_player(ctx)
        music_info = await player.get_ifo_music(song_url, self.bot.loop)
        print(music_info)
        if len(music_info) == 0:
            await ctx.send(f"error al buscar s{song_url}", delete_after=5)

        if (d := music_info['duration']) >= 422:
            await ctx.send("La canción dura mas de `7:00 min`, ***zzzzz***")
        else:
            url = music_info['formats'][0]['url']
            title = music_info['title']
            duration = h.get_duration(d)
            source = await FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            await player.queue.put({"s": source, "u": url, "t": title, "d": duration, "a": ctx.author, "l": song_url})
            await ctx.send(f"```diff\n+ 💿 {title} agregado a la cola...```", delete_after=5)

    @commands.command(name="queue", aliases=["q"], description="show music queue")
    @commands.guild_only()
    async def queue(self, ctx):
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            return await ctx.send('No te encuentras en un canal de voz', delete_after=5)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('Actualmente la cola está vacía')

        # accediendo a la variable privada del objeto asyncio.Queue(), retorna la lista de la Cola
        music_queue = list(player.queue._queue)
        next_music_info = music_queue.pop(0)
        next_music = f"\n+▶{next_music_info['t']} by:[{next_music_info['a']}] 👈next"
        content = '\n'.join(f'+▶{m["t"]} by:[{m["a"]}]' for m in music_queue)
        #embed = Embed(title=f' tam:{len(music_queue)}', description= f"```diff\n{content}\n```")
        #await ctx.send(embed=embed, delete_after=10)
        await ctx.send(f"😎😎😎```diff\n+QUEUE longitud:`{len(music_queue) + 1}"
                       f"`{next_music}\n{content}\n```", delete_after=30)

    @commands.command(name='pause', aliases=["ps"], description="pause the song")
    @commands.guild_only()
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await ctx.send('No hay nada reproduciendose, tu tampoco debes reproducirte!', delete_after=20)
        elif voice_client.is_paused():
            return
        voice_client.pause()
        await ctx.send(f'**`{ctx.author}`**: ese gil puso pausa')

    @commands.command(name="stop", aliases=["s", "d"], description="stop music and disconect")
    @commands.guild_only()
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send('No hay nada reproduciendose, tu tampoco debes reproducirte!', delete_after=20)
        await self.cleanup(ctx.guild)

    @commands.command(name="resume", aliases=["r"], description="restart stop music")
    @commands.guild_only()
    async def resume(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send('no hay nada en `pause`!!!', delete_after=20)
        elif not voice_client.is_paused():
            return
        voice_client.resume()
        await ctx.send(f'**`{ctx.author}`**: reanudando')

    @commands.command(name="next", aliases=["n"], description="next music")
    @commands.guild_only()
    async def next(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send('???', delete_after=10)
        if voice_client.is_paused():
            pass
        elif not voice_client.is_playing():
            return
        voice_client.stop()
        await ctx.send(f'**`{ctx.author}`**: cambió la rola')

    @commands.command(name="clear", aliases=["c"], description="clear queue")
    @commands.guild_only()
    async def clear(self, ctx) -> None:
        if not (voice_client := ctx.voice_client):
            return await ctx.send('???', delete_after=10)
        player = self.get_player(ctx)
        if voice_client.is_connected() and not player.queue.empty():
            for source in player.queue._queue:
                if isinstance(source, FFmpegOpusAudio):
                    source.cleanup()
            self.music_players[ctx.guild.id].queue._queue.clear()
            await ctx.send(f'**`{ctx.author}`**: vació la cola de reproducción')

    @commands.command(name="fav", aliases=["f"], description="add name or link fav music")
    @commands.guild_only()
    async def add_fav(self, ctx, song) -> None:
        # en teoría para usaurios premiun, o que verifique que tengan el rol de de vip
        pass


def setup(bot):
    bot.add_cog(DJ(bot))
