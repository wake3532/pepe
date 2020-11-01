import os,logging, asyncio, random, itertools, math, time
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from async_timeout import timeout
import functools
from functools import partial
import youtube_dl
from youtube_dl import YoutubeDL
from io import StringIO
import os
import youtube_dl

##################### 로깅 ###########################
log_stream = StringIO()    
logging.basicConfig(stream=log_stream, level=logging.WARNING)

#result_log = logging.getLogger('discord')
#result_log.setLevel(level = logging.WARNING)
#handler = logging.StreamHandler()
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#result_log.addHandler(handler)
#####################################################

access_token = "your_token_here"

def _prefix_callable(bot, msg):
	if msg.author.bot:
		return None
	base = []
	base.extend(bot.prefixes[msg.guild.id])
	return base

class MusicBot(commands.AutoShardedBot):
	def __init__(self):
		self.default_prefix = ["!"]
		self.prefixes = {}
		
		super().__init__(command_prefix = _prefix_callable, help_command = None)
	
	def run(self):
		super().run(access_token, reconnect = True)

	async def on_ready(self):
		print("Logged in as ")
		print(self.user.name)
		print(self.user.id)
		print("===========")

		for guild in self.guilds:
			self.prefixes[guild.id] = self.default_prefix

		await self.change_presence(status = discord.Status.online, activity = discord.Game(name = "뮤직봇", type = 1), afk = False)

	async def set_guild_prefixes(self, guild, prefixes):
		if len(prefixes) == 0:
			self.prefixes[guild.id] = ["!"]
		elif len(prefixes) > 10:
			raise RuntimeError(" 등록된 접두사가 10개가 넘어요 . <:Blobastnoished:767031123778863125>  ")
		else:
			self.prefixes[guild.id] = prefixes

	async def on_command_error(self, ctx, error):
		if isinstance(error, CommandNotFound):
			return
		elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
			return
		raise error

	async def close(self):
		await super().close()
		print(" 뮤직봇을 정상 종료했어요 <:Blobokhand:767031123812417548>   ")

youtube_dl.utils.bug_reports_message = lambda: ""

class VoiceError(Exception):
	pass

class YTDLError(Exception):
	pass

class YTDLSource(discord.PCMVolumeTransformer):
	YTDL_OPTIONS = {
		'format': 'bestaudio/best',
		'extractaudio': True,
		'audioformat': 'mp3',
		'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
		'restrictfilenames': True,
		'noplaylist': False,
		'nocheckcertificate': True,
		'ignoreerrors': False,
		'logtostderr': False,
		'quiet': True,
		'no_warnings': True,
		'default_search': 'auto',
		'source_address': '0.0.0.0',
		'force-ipv4' : True,
			'-4': True
	}
	FFMPEG_OPTIONS = {
		'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
		'options': '-vn',
	}

	ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

	def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, data: dict, *,volume: float = 0.5):
		super().__init__(source, volume)
		self.requester = ctx.author
		self.channel = ctx.channel
		self.data = data

		self.uploader = data.get('uploader')
		self.uploader_url = data.get('uploader_url')
		self.date = data.get('upload_date')
		self.upload_date = self.date[6:8] + '.' + self.date[4:6] + '.' + self.date[0:4]
		self.title = data.get('title')
		self.thumbnail = data.get('thumbnail')
		self.description = data.get('description')
		self.duration = self.parse_duration(int(data.get('duration')))
		self.tags = data.get('tags')
		self.url = data.get('webpage_url')
		self.stream_url = data.get('url')

	def __str__(self):
		return "**{0.title}** by **{0.uploader}**".format(self)

	@classmethod
	async def create_source(cls, bot, ctx : commands.Context, search : str, *, loop : asyncio.BaseEventLoop = None):
		loop = loop or asyncio.get_event_loop()

		if "http" not in search:
			partial = functools.partial(cls.ytdl.extract_info, f"ytsearch5:{search}", download = False, process = False)

			data = await loop.run_in_executor(None, partial)

			if data is None:
				raise YTDLError(f"<:Blobfacebalm:767031123258900531>  **{search}** 를 열심히 찾아봤지만 도저히 못 찾겠어요 죄송해요  ")

			emoji_list : list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "🚫"]
			song_list_str : str = ""
			cnt : int = 0
			song_index : int = 0

			for data_info in data["entries"]:
				cnt += 1
				if "title" not in data_info:
					data_info["title"] = f"{search} - 정보 없음 "
				song_list_str += f"`{cnt}.` [**{data_info['title']}**](https://www.youtube.com/watch?v={data_info['url']})\n"

			embed = discord.Embed(description = song_list_str)
			embed.set_footer(text = f"10초 안에 미선택시 취소됩니다.")

			song_list_message = await ctx.send(embed = embed)

			for emoji in emoji_list:
				await song_list_message.add_reaction(emoji)

			def reaction_check(reaction, user):
				return (reaction.message.id == song_list_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
			try:
				reaction, user = await bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
			except asyncio.TimeoutError:
				reaction = "🚫"

			for emoji in emoji_list:
				await song_list_message.remove_reaction(emoji, bot.user)

			await song_list_message.delete(delay = 10)
			
			if str(reaction) == "1️⃣":
				song_index = 0
			elif str(reaction) == "2️⃣":
				song_index = 1
			elif str(reaction) == "3️⃣":
				song_index = 2
			elif str(reaction) == "4️⃣":
				song_index = 3
			elif str(reaction) == "5️⃣":
				song_index = 4
			else:
				return False
			
			result_url = f"https://www.youtube.com/watch?v={data['entries'][song_index]['url']}"
		else:
			result_url = search

		webpage_url = result_url
		partial = functools.partial(cls.ytdl.extract_info, webpage_url, download = False)
		processed_info = await loop.run_in_executor(None, partial)
		if processed_info is None:
			raise YTDLError("Couldn\'t fetch `{}`".format(webpage_url))
		
		if "entries" not in processed_info:
			info = processed_info
		else:
			info = None
			while info is None:
				try:
					info = processed_info['entries'].pop(0)
				except IndexError:
					raise YTDLError(f"`{webpage_url}`는 없는 검색 결과예요")

		return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data = info)

	@staticmethod
	def parse_duration(duration : int):
		return time.strftime("%H:%M:%S", time.gmtime(duration))

class Song:
	__slots__ = ("source", "requester")

	def __init__(self, source: YTDLSource):
		self.source = source
		self.requester = source.requester

	def create_embed(self):
		embed = discord.Embed(title = 'Now playing', description = f"**```fix\n{self.source.title}\n```**", color = discord.Color.blurple())
		embed.add_field(name = 'Duration', value = self.source.duration)
		embed.add_field(name = 'Requested by', value = self.requester.mention)
		embed.add_field(name = 'Uploader', value = f"[{self.source.uploader}]({self.source.uploader_url})")
		embed.add_field(name = 'URL', value = f"[Click]({self.source.url})")
		embed.set_thumbnail(url = self.source.thumbnail)
		return embed

class SongQueue(asyncio.Queue):
	def __getitem__(self, item):
		if isinstance(item, slice):
			return list(itertools.islice(self._queue, item.start, item.stop, item.step))
		else:
			return self._queue[item]

	def __iter__(self):
		return self._queue.__iter__()

	def __len__(self):
		return self.qsize()

	def clear(self):
		self._queue.clear()

	def shuffle(self):
		random.shuffle(self._queue)

	def select(self, index : int, loop : bool = False):
		for i in range(index-1):
			if not loop:
				del self._queue[0]
			else:
				self._queue.append(self._queue[0])
				del self._queue[0]

	def remove(self, index: int):
		del self._queue[index]

class VoiceState:
	def __init__(self, bot: commands.Bot, ctx: commands.Context):
		self.bot = bot
		self._ctx = ctx
		self._cog = ctx.cog

		self.current = None
		self.voice = None
		self.next = asyncio.Event()
		self.songs = SongQueue()

		self._loop = False
		self._volume = 0.5

		self.audio_player = bot.loop.create_task(self.audio_player_task())

	def __del__(self):
		self.audio_player.cancel()

	@property
	def loop(self):
		return self._loop

	@loop.setter
	def loop(self, value : bool):
		self._loop = value

	@property
	def volume(self):
		return self._volume

	@volume.setter
	def volume(self, value : float):
		self._volume = value

	@property
	def is_playing(self):
		return self.voice and self.current

	async def audio_player_task(self):
		while True:
			self.next.clear()

			if self.loop and self.current is not None:
				source1 = await YTDLSource.create_source(self.bot, self._ctx, self.current.source.url, loop=self.bot.loop)
				song1 = Song(source1)
				await self.songs.put(song1)
			else:
				pass

			try:
				async with timeout(180): 
					self.current = await self.songs.get()
			except asyncio.TimeoutError:
				self.bot.loop.create_task(self.stop())
				return

			self.current.source.volume = self._volume
			self.voice.play(self.current.source, after = self.play_next_song)
			play_info_msg = await self.current.source.channel.send(embed = self.current.create_embed())
			await play_info_msg.delete(delay = 20)

			await self.next.wait()

	def play_next_song(self, error = None):
		if error:
			raise VoiceError(str(error))

		self.next.set()

	def skip(self):

		if self.is_playing:
			self.voice.stop()

	async def stop(self):
		self.songs.clear()

		if self.voice:
			await self.voice.disconnect()
			self.voice = None

		self.bot.loop.create_task(self._cog.cleanup(self._ctx))

class Music(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot
		self.voice_states = {}

	def get_voice_state(self, ctx : commands.Context):
		state = self.voice_states.get(ctx.guild.id)
		if not state:
			state = VoiceState(self.bot, ctx)
			self.voice_states[ctx.guild.id] = state
		return state

	def cog_unload(self):
		for state in self.voice_states.values():
			self.bot.loop.create_task(state.stop())

	def cog_check(self, ctx : commands.Context):
		if not ctx.guild:
			raise commands.NoPrivateMessage("<:Blobfacebalm:767031123258900531>  OOPS ! 에러 발생! ")
		return True

	async def cog_before_invoke(self, ctx : commands.Context):
		ctx.voice_state = self.get_voice_state(ctx)

	async def cog_command_error(self, ctx : commands.Context, error : commands.CommandError):
		await ctx.send(f"에러 : {str(error)}")

	async def cleanup(self, ctx : commands.Context):
		del self.voice_states[ctx.guild.id]

	@commands.command(name = "join", aliases = ["ㄷㄱ"])
	#@commands.has_permissions(manage_guild=True)
	async def summon_(self, ctx : commands.Context, *, channel : discord.VoiceChannel = None):
		"""<:Blobokhand:767031123812417548> 들어갔어요 저를 환영해주세요 ㅎㅎ """
		if not channel and not ctx.author.voice:
			raise VoiceError("<:Blobdizzy:767031123590643712> 현재 접속중인 음성 채널이 없어요! 삐빅 ")

		destination = channel or ctx.author.voice.channel
		if ctx.voice_state.voice:
			await ctx.voice_state.voice.move_to(destination)
			return

		ctx.voice_state.voice = await destination.connect()

	@commands.command(name = "stop", aliases = ["ㄴㄱ"])
	#@commands.has_permissions(manage_guild=True)
	async def leave_(self, ctx : commands.Context):
		"""<:Blobokhand:767031123812417548> 음성채널에서 나갔어요"""
		if not ctx.voice_state.voice:
			return await ctx.send("<:Blobdizzy:767031123590643712> 저랑 당신이랑 같이 있지 않아요 🙀")

		await ctx.voice_state.stop()
		del self.voice_states[ctx.guild.id]

	@commands.command(name = "Volume", aliases = ["ㅂㄹ"])
	async def volume_(self, ctx : commands.Context, *, volume : int):
		"""<:Blobokhand:767031123812417548> 조절을 완료 했어요 """
		if not ctx.voice_state.is_playing:
			return await ctx.send("<:Blobfacebalm:767031123258900531>  현재 재생중인 음악이 없어요 :(")

		if not 0 < volume < 101:
			return await ctx.send(" 1~100으로 해주세요 ㅣ 귀가 너무 아프시면 안되잖아요! ㅎㅎㅎㅎ <:Hyperthink:767031123867729931>  ")

		if ctx.voice_client.source:
			ctx.voice_client.source.volume = volume / 100

		ctx.voice_state.volume = volume / 100
		await ctx.send(f"<:Blobokhand:767031123812417548> 볼륨을  **{volume}%** 로 완료했어요")

	@commands.command(name="재생정보", aliases=["ㅈㅅㅈㅂ"])
	async def now_(self, ctx : commands.Context):
		"""재생 정보예요. 너무 좋은거 같아요! ㅎ!!! """
		await ctx.send(embed = ctx.voice_state.current.create_embed())

	@commands.command(name="일시정지", aliases=["ㅇㅅㅈㅈ"])
	#@commands.has_permissions(manage_guild=True)
	async def pause_(self, ctx : commands.Context):
		"""<:Phappy:767031123851083867>  일시정지를 정상적으로 완료했어요   """
		if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
			ctx.voice_state.voice.pause()
			await ctx.message.add_reaction("⏸")

	@commands.command(name = "다시재생", aliases = ["ㄷㅅㅈㅅ"])
	#@commands.has_permissions(manage_guild=True)
	async def resume_(self, ctx : commands.Context):
		"""일시정지 중인 노래 다시재생"""
		if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
			ctx.voice_state.voice.resume()
			await ctx.message.add_reaction("⏯")

	@commands.command(name = "정지", aliases = ["ㅈㅈ"])
	#@commands.has_permissions(manage_guild=True)
	async def stop_(self, ctx : commands.Context):
		"""재생 중인 노래 정지"""
		ctx.voice_state.songs.clear()

		if ctx.voice_state.is_playing:
			ctx.voice_state.voice.stop()
			await ctx.message.add_reaction("⏹")

	@commands.command(name = "스킵", aliases = ["ㅅㅋ"])
	async def skip_(self, ctx: commands.Context, *, args: int = 1):
		"""재생 중인 노래 스킵, 숫자 입력시 해당 노래까지 스킵 : prefix + 스킵 (숫자)"""
		if not ctx.voice_state.is_playing:
			return await ctx.send("재생중인 노래 또는 다음 노랴가 없어요 .")

		await ctx.message.add_reaction("⏭")

		if args != 1:
			ctx.voice_state.songs.select(args, ctx.voice_state.loop)

		ctx.voice_state.skip()

	@commands.command(name = "목록", aliases = ["ㅁㄹ"])
	async def queue_(self, ctx : commands.Context, *, page : int = 1):
		"""재생목록 불러오기 1페이지 당 10개 표시, 숫자입력히 해당 페이지 표시 : prefix + 목록 (숫자)"""
		if len(ctx.voice_state.songs) == 0:
			return await ctx.send(" <:Phappy:767031123851083867>  재생목록이 없어요!! ")
		
		items_per_page = 10
		pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

		start = (page - 1) * items_per_page
		end = start + items_per_page

		queue = ""
		for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
			queue += f"`{i + 1}.` [**{song.source.title}**]({song.source.url})\n"

		if ctx.voice_state.loop:
			embed = discord.Embed(title = f"🔁  Now playing', description=f'**```fix\n{ctx.voice_state.current.source.title}\n```**")
		else:
			embed = discord.Embed(title = f"Now playing', description=f'**```fix\n{ctx.voice_state.current.source.title}\n```**")
		embed.add_field(name = f"\u200B\n**{len(ctx.voice_state.songs)} tracks:**\n", value = f"\u200B\n{queue}")
		embed.set_thumbnail(url = ctx.voice_state.current.source.thumbnail)
		embed.set_footer(text = f"Viewing page {page}/{pages}")
		await ctx.send(embed = embed)


	@commands.command(name = "삭제", aliases = ["ㅅㅈ"])
	async def remove_(self, ctx : commands.Context, index : int):
		"""재생목록에 등록된 노래 삭제 : prefix + 삭제 [숫자]"""
		if len(ctx.voice_state.songs) == 0:
			return await ctx.send("재생목록이 없습니다.")
		
		remove_result = f"`{index}.` [**{ctx.voice_state.songs[index - 1].source.title}**] 삭제 정상적으로 완료! ! <:Blobokhand:767031123812417548> \n"
		result = await ctx.send(remove_result)
		ctx.voice_state.songs.remove(index - 1)
		await result.add_reaction('✅')
		

	@commands.command(name = "반복", aliases = ["ㄹㅍ"])
	async def loop_(self, ctx : commands.Context):
		"""재생목록 반복"""
		if not ctx.voice_state.is_playing:
			return await ctx.send(" 무엇을 반복하면 되나요 ??? <:Blobfrowning:767031123241992224>   ")

		# Inverse boolean value to loop and unloop.
		ctx.voice_state.loop = not ctx.voice_state.loop
		if ctx.voice_state.loop:
			result = await ctx.send("<:Blobokhand:767031123812417548>  이제부터 이 노래를 반복으로 틀을께요! ")
		else:
			result = await ctx.send("<:Blobokhand:767031123812417548>  반복재생이 취소되었습니다!")
		await result.add_reaction('🔁')

	@commands.command(name = "play", aliases = ["p", "P", "ㅔ"])
	async def play_(self, ctx : commands.Context, *, search : str):
		"""검색어, url로 노래 검색"""
		if not ctx.voice_state.voice:
			await ctx.invoke(self.summon_)

		async with ctx.typing():
			try:
				source = await YTDLSource.create_source(self.bot, ctx, search, loop = self.bot.loop)
				if not source:
					return await ctx.send(f"노래 재생/예약이 취소 되었습니다.")
			except YTDLError as e:
				await ctx.send(f"에러가 발생했습니다 : {str(e)}")
			else:
				song = Song(source)

				await ctx.voice_state.songs.put(song)
				await ctx.send(f"재생목록 추가 : {str(source)}")


	@commands.command(name = "접두사 변경", aliases = ["ㅍㄹ"])
	async def prefix_add_(self, ctx: commands.Context, *, prefix : str):
		"""프리픽스 변경, 최대 10개 등록 가능"""
		if not prefix:
			return await ctx.send(f"변경할 prefix를 입력하세요.")

		prefix_list = prefix.split()

		await self.bot.set_guild_prefixes(ctx.guild, prefix_list)
		await ctx.send(f"<:Blobokhand:767031123812417548>  접두사를 **[{prefix}]**로 바꿨어요 ")

	@commands.command(name = "종료", aliases = ["ㅈㄹ"])
	async def shutdown_(self, ctx: commands.Context):
		"""봇 종료"""
		await ctx.send("뮤직봇 종료")
		return await self.bot.close()

	@summon_.before_invoke
	@play_.before_invoke
	async def ensure_voice_state(self, ctx : commands.Context):
		if not ctx.author.voice or not ctx.author.voice.channel:
			raise commands.CommandError("<:Blobping:767031123494174721>  음성채널에 가입되어 있지 않네요 ! ")

		if ctx.voice_client:
			if ctx.voice_client.channel != ctx.author.voice.channel:
				raise commands.CommandError("<:Phappy:767031123851083867>  이미 가입 완료했어요 ")

music_bot : MusicBot = MusicBot()
music_bot.add_cog(Music(music_bot))
                
access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
