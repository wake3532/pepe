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


client = discord.Client()

@client.event
async def on_ready():
    print('봇이 로그인 하였습니다.')
    print(' ')
    print('닉네임 : {}'.format(client.user.name))
    print('아이디 : {}'.format(client.user.id))

@client.event
async def on_ready():
    print('봇이 로그인 하였습니다.')
    print(' ')
    print('닉네임 : {}'.format(client.user.name))
    print('아이디 : {}'.format(client.user.id))
    while True:
        user = len(client.users)
        server = len(client.guilds)
        messages = ["NICE", "FUCK YOU" , "HAHA LOL " , str(user) + "명은 FUCK YOU .", str(server) + "명은 내꼬"]
        for (m) in range(5):
            await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(name=messages[(m)], type=discord.ActivityType.watching))
            await asyncio.sleep(4)


@client.event
async def on_member_remove(member):
    try:
        syscha = member.guild.system_channel
        await syscha.send(member.name + "님이 ``" + member.guild.name + "`` 서버에서 나가셨습니다.ㅠㅠㅠㅠ SADDD  <:Blobfacebalm:767031123258900531>  ")
    except:
        pass

@client.event
async def on_message(message):
    if message.content.startswith("t/mute"):
        if message.author.guild_permissions.administrator:
            firstid = message.content[4:]
            author = message.guild.get_member(int(firstid[2:20]))
            role = discord.utils.get(message.guild.roles, name="뮤트")
            await author.add_roles(role)
            await message.channel.send("<:Blobokhand:767031123812417548>  http://gph.is/2bDfI0R ** MUTE DONE ** ")
        else:
            await message.channel.send("**관리자 권한 거부**")

    if message.content.startswith("t/unmute"):
        if message.author.guild_permissions.administrator:
            firstid = message.content[5:]
            author = message.guild.get_member(int(firstid[2:20]))
            role = discord.utils.get(message.guild.roles, name="뮤트")
            await author.remove_roles(role)
            await message.channel.send("https://gph.is/2HPTFD1  <:Blobokhand:767031123812417548>  **speak!**")
        else:
            await message.channel.send("**관리자 권한 거부**")
	
access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
