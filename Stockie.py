import discord
import os
import asyncio
import random
import json
import datetime
from asyncio import tasks
from asyncio.tasks import Task, ensure_future
from discord.ext import tasks, commands


client = commands.Bot(command_prefix='.')
client.remove_command('help')

@client.event
async def on_ready(): 
  print("We have logged in as {0.user}".format(client))
  print("Stock Bot has awoken")
    
      
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'for .help'))

@client.command()
async def stockie(ctx):
  await ctx.send("hi, thats me!")


client.run(os.getenv("OTYyMDU0MTgzMzA4MTIwMDg0.YlB8xw.1u9EuuTtSrWj5BqiKc39csc-QRw"))
