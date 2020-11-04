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
        messages = ["안녕하세요. ", "🌷 " , "👋  " , str(user) + "명이 우리 서버 가입중이라니. 참 기분이 좋아요..!  .", str(server) + "명이 부스트를 해주셨어요. 고마워요!"]
        for (m) in range(5):
            await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(name=messages[(m)], type=discord.ActivityType.watching))
            await asyncio.sleep(4)
		
		
@client.event
async def on_member_join(member):
    try:
        syscha = member.guild.system_channel
        await syscha.send(f"{member.mention} 님 어서오세요! 🥳 ")
    except:
        pass

@client.event
async def on_member_remove(member):
    try:
        syscha = member.guild.system_channel
        await syscha.send(member.name + "님 ``" + member.guild.name + "`` 안녕히가세요 ㅜ.. 😭")
    except:



@client.event
async def on_message(message):
	
 if message.content.startswith("t/dm0777"):
    message = message.content[4:]
    getusermention = client.get_user(아이디)
    await getusermention.send(message)

	
access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
