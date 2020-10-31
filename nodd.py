import discord
from discord.ext import commands
import os
import asyncio
import random
import urllib
from bs4 import BeautifulSoup
from urllib.request import Request
from urllib import parse
import bs4
import time
import random

client = discord.Client()

@client.event
async def on_ready():
    print("봇이 정상적으로 실행되었습니다.")
    game = discord.Game('GOODDDDDDDDDDDDDDDDDDDDDDDD XDD ⭐')
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_member_join(member):
    try:
        syscha = member.guild.system_channel
        await syscha.send(f"{member.mention} https://gph.is/g/aXJQgDO <:Blobcheer:767031123543982101>  ")
    except:
        pass

@client.event
async def on_member_remove(member):
    try:
        syscha = member.guild.system_channel
        await syscha.send(member.name + "님이 서버에서 나가셨어요.  ``" + member.guild.name + "<:Blobdrool:767031123535593472>  https://gph.is/2RY0k2q  ")
    except:
        pass

@client.event
async def on_message(message):
    if message.content.startswith("t/뮤트"):
        if message.author.guild_permissions.administrator:
        firstid = message.content[4:]
        author = message.guild.get_member(int(firstid[2:20]))
        role = discord.utils.get(message.guild.roles, name="뮤트")
        await author.add_roles(role)
        await message.channel.send("<:Blobokhand:767031123812417548>  **뮤트를 완료했어요 이상한 사람이 있으면 그냥 바로 밴이나 뮤트를 해야해요. **")
    else:
        await message.channel.send("<:Blobcry:767031123549093918> ** 뮤트를 완료하지 못 했어요 죄송해요 :(  **")

    if message.content.startswith("t/언뮤트"):
        if message.author.guild_permissions.administrator:
        firstid = message.content[5:]
        author = message.guild.get_member(int(firstid[2:20]))
        role = discord.utils.get(message.guild.roles, name="뮤트")
        await author.remove_roles(role)
        await message.channel.send("<:Blobokhand:767031123812417548> **뮤트를 해제했어요. 이제 당신이 푼 사용자는 이제 말 할 수 있어요. ** ")
    else:
        await message.channel.send("<:Blobcry:767031123549093918> ** 언뮤트를 완료하지 못 했어요 죄송해요 :(  **")

    if message.content.startswith('t!/기본유저역할확인'):
        for i in message.author.roles:
            if i.name == '유저':
                await message.channel.send('<:Blobsmile:767031123682263060>  굳! 역할을 가지고 있어요.')
                break

    if message.content == "t/mp3play":
        if not message.attachments:
            pass
        else:
            try:
                mp3 = message.attachments[0]
                await mp3.save(mp3.filename)
                channel = message.author.voice.channel
                player = await channel.connect()
            
                if player.is_playing():
                    player.stop()
                player.play(discord.FFmpegPCMAudio(source=mp3.filename))
                await message.channel.send(f'<:Blobhearteyes:767031123586580520>  MP3파일을 재생했어요. 너무 좋아서 취하는 느낌이에요... 파일명 💿 : **{mp3.filename}** 을 재생중이에요 ! 😉 ')
                os.remove(mp3.filename)
            except:
                pass

    if message.content.startswith(''):
            vote = message.content[4:].split("t/vote")
            await message.channel.send("<:Blobgrin:767031123611615262>  **투표 부탁드립니다! **" + vote[0] + "**")
            for i in range(1, len(vote)):
                choose = await message.channel.send("**" + vote[i] + "**")
                await choose.add_reaction('👍')
                await choose.add_reaction('👎')