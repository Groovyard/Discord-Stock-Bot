#Imports
import discord
import os
import asyncio
import math
import random
import json
import datetime
import requests
import pandas as pd
import time
from asyncio import tasks
from datetime import datetime
from asyncio.tasks import Task, ensure_future
from discord.ext import tasks, commands
from keep_alive import keep_alive

#Setting Up !Help
client = commands.Bot(command_prefix='!')
client.remove_command('help')

@client.event
async def on_ready(): 
  print("We have logged in as {0.user}".format(client))
  print("StocksQuest Bot has awoken")
  
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'for !help'))

#Introductry Message From Bot
@client.command()
async def stocks(ctx):
  await ctx.send("Hi, Hope Your Doing Well!")

name = ""

#Setting up API Integration
#Credits to TwelveData for the API
@client.command(aliases = ["p"])
async def price(ctx, *args):
  ticker = args[0]

  api_key = "45cccf85d76244f383cce8624d875426"

  def get_stock_price(ticker_symbol, api):
      url = f"https://api.twelvedata.com/price?symbol={ticker_symbol}&apikey={api}"
      response = requests.get(url).json()
      price = response['price'][:-3]
      return price
  
  
  def get_stock_quote(ticker_symbol, api):
      url = f"https://api.twelvedata.com/quote?symbol={ticker_symbol}&apikey={api}"
      response = requests.get(url).json()
      return response
  
  stockdata = get_stock_quote(ticker, api_key)
  stock_price = get_stock_price(ticker, api_key)
  
  name = stockdata['name']
  price = (stock_price)

  em = discord.Embed(title = f"{name}", color = discord.Color.green())
  em.add_field(name = "Cost in USD",value = "$" + price)
  
  await ctx.send(embed = em)

@client.command()
async def say(ctx, *args):
    one_word_per_line = '\n'.join(args)
    quote_text = 'You said:\n>>> {}'.format(one_word_per_line)
    await ctx.send(quote_text)

#!help command
@client.group(invoke_without_command=True)
async def help(ctx):
  em = discord.Embed(title = "Commands", description = "Use *!help*<command> for more information on each command!\nExamples of stocks are - AMZN, TSLA, TD, AC, MSFT, AAPL (lowercase is allowed)", color = ctx.author.color)

  em.add_field(name = "!balance (!bal)", value = "View your account's balance (USD)", inline=False)
  em.add_field(name = "!leaderboard (!lb)", value = "Check the leaderboard for the users on top!", inline=False)
  em.add_field(name = "!price (!p)", value = "Perform !price [stock_name], to see the price of the stock!", inline=False)
  em.add_field(name = "!buy (!b)", value = "Use command to buy stocks, enter !b [stock_name]", inline=False)
  em.add_field(name = "!help", value = "View the help page for more information on commands", inline=False)
  em.add_field(name = "!stocks (!st)", value = "View the amount of stocks that you own!", inline=False)
  em.add_field(name = "!sell (!s)", value = "Use command to sell stocks, enter !b [stock_name]", inline=False)
  em.add_field(name = "!work (!w)", value = "Every 8 hours you can work and earn money", inline=False)
  
  await ctx.send(embed = em)

#!Paycheck - Work Command
@client.command(aliases=["work"])
async def w(ctx):
  await time_account(ctx.author)
  timer = ctx.author
  timers = await get_time_data()
  await bank_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  
  now = datetime.now()
  format = now.strftime("%d/%m/%Y %H:%M:%S")
  current_day = now.strftime("%d")
  current_month = now.strftime("%m")
  current_year = now.strftime("%Y")
  current_hour = now.strftime("%H")
  current_minute = now.strftime("%M")
  year = (int(current_year)*525600)
  month = (int(current_month)*43800)
  day = (int(current_day)*1440)
  hour = (int(current_hour)*60)
  minute = (int(current_minute))
  total = (year + month + day + hour + minute)
  
  wage = random.randrange(14, 23)
  daily = (wage*8)
  a = total - int(timers[str(timer.id)]["minutes"])
  b = 480 - a
  c = math.floor(b/60)
  d = (b - (c*60))
  
  if timers[str(timer.id)]["minutes"] == total:
    await ctx.send("You're time is not up yet")
    await ctx.send(f"**{c} hours** and **{d} minutes** left, come back later")
  else: 
    timers[str(timer.id)]["minutes"] = (total)
    await ctx.send(f"You have worked and earned ${daily}! Come back after 8 hours.")
    users[str(user.id)]["balance"] += daily
    
  with open("work.json", "w") as f:
    json.dump(timers, f)
  with open("balance.json", "w") as f:
    json.dump(users, f)

#Buying & Selling Stock Commands
    
#Setting up !Buy Command
@client.command(aliases=["buy"])
async def b(ctx, *args):
  ticker = args[0]

  api_key = "45cccf85d76244f383cce8624d875426"

  def get_stock_price(ticker_symbol, api):
      url = f"https://api.twelvedata.com/price?symbol={ticker_symbol}&apikey={api}"
      response = requests.get(url).json()
      price = response['price'][:-3]
      return price
  
  def get_stock_quote(ticker_symbol, api):
      url = f"https://api.twelvedata.com/quote?symbol={ticker_symbol}&apikey={api}"
      response = requests.get(url).json()
      return response
  
  stockdata = get_stock_quote(ticker, api_key)
  stock_price = get_stock_price(ticker, api_key)
  
  name = stockdata['name']
  price = (stock_price)
  
  await stock_account(ctx.author)
  acc = ctx.author
  accs = await get_stock_data()
  await bank_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()

  bal = users[str(user.id)]["balance"]
  
  if bal >= float(price):
    users[str(user.id)]["balance"] -= float(price)
    if (f"{name}" in accs[str(acc.id)]):
      accs[str(acc.id)][f"{name}"] += 1
    else:
      accs[str(acc.id)][f"{name}"] = 1
    await ctx.send(f"You have purchased 1 share of {name} for ${price}!")
  else:
    await ctx.send("Not enough money!")
  
  with open("balance.json", "w") as f:
    json.dump(users, f)
  with open("stocks.json", "w") as f:
    json.dump(accs, f)

#Setting up !Sell Command    
@client.command(aliases=["sell"])
async def s(ctx, *args):
  ticker = args[0]

  api_key = "45cccf85d76244f383cce8624d875426"

  def get_stock_price(ticker_symbol, api):
      url = f"https://api.twelvedata.com/price?symbol={ticker_symbol}&apikey={api}"
      response = requests.get(url).json()
      price = response['price'][:-3]
      return price
  
  def get_stock_quote(ticker_symbol, api):
      url = f"https://api.twelvedata.com/quote?symbol={ticker_symbol}&apikey={api}"
      response = requests.get(url).json()
      return response
  
  stockdata = get_stock_quote(ticker, api_key)
  stock_price = get_stock_price(ticker, api_key)
  
  name = stockdata['name']
  price = (stock_price)
  
  await stock_account(ctx.author)
  acc = ctx.author
  accs = await get_stock_data()
  await bank_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  
  with open ("stocks.json") as fp:
    list = json.load(fp)
  
  if (f"{name}" in accs[str(acc.id)]):
    if accs[str(acc.id)][f"{name}"] <= 0:
      await ctx.send("You do not have that stock!")
    else:
      accs[str(acc.id)][f"{name}"] -= 1
      users[str(user.id)]["balance"] += float(price)
      await ctx.send(f"You have sold 1 share of {name} for ${price}!")
    
  else:
    await ctx.send("You do not have that stock!")
  
  with open("balance.json", "w") as f:
    json.dump(users, f)
  with open("stocks.json", "w") as f:
    json.dump(accs, f)    

    
#stock
@client.command(aliases=["stock"])
async def st(ctx):
  await stock_account(ctx.author)
  acc = ctx.author
  accs = await get_stock_data()
  
  em = discord.Embed(title = f"{ctx.author.name}'s Stocks", color = discord.Color.green())
  
  for i in accs[str(acc.id)]:
    em.add_field(name = f"{i}",value = accs[str(acc.id)][i])

  await ctx.send(embed = em)
  
#!Balance - Showing balance of user command.
@client.command(aliases=["balance"])
async def bal(ctx):
  await bank_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()

  balance_amt = users[str(user.id)]["balance"]
  
  em = discord.Embed(title = f"{ctx.author.name}'s balence", color = discord.Color.green())
  em.add_field(name = "Balance (USD)",value = "$" + str(balance_amt))
  await ctx.send(embed = em)

#general command
async def bank_account(user):
    
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["balance"] = 1000
  
    with open("balance.json", "w") as f:
        json.dump(users, f)
    return True


async def get_bank_data():
    with open("balance.json", "r") as f:
        users = json.load(f)
    
    return users

async def stock_account(acc):
    
    accs = await get_stock_data()

    if str(acc.id) in accs:
        return False
    else:
        accs[str(acc.id)] = {}
  
    with open("stocks.json", "w") as f:
        json.dump(accs, f)
    return True

async def get_stock_data():
    with open("stocks.json", "r") as f:
        accs = json.load(f)
    
    return accs


async def time_account(timer):
    
    timers = await get_time_data()

    if str(timer.id) in timers:
        return False
    else:
        timers[str(timer.id)] = {}
        timers[str(timer.id)]["minutes"] = 10000000000000000000000000000000000000000
  
    with open("work.json", "w") as f:
        json.dump(timers, f)
    return True

async def get_time_data():
    with open("work.json", "r") as f:
        timers = json.load(f)
    
    return timers
  
  
#!leaderboard - Shows leaderboard command.
@client.command(aliases = ["lb"])
async def leaderboard(ctx, x=10):
    users = await get_bank_data()
    
    d = {user_id: info["balance"] for user_id, info in users.items()}
    leaderboard = {user_id: amount for user_id, amount in sorted(d.items(), key=lambda item: item[1], reverse=True)}

    embed = discord.Embed(
        title = f"Top {x} Richest People",
        description = "Ranking of most richest people",
        color = discord.Colour.green()
    )

    for index, infos in enumerate(leaderboard.items()):
        user_id, amount = infos
        member = await client.fetch_user(user_id)
        name = member.name
        if index == 0:
          continue
        embed.add_field(
            name = f"{index}. {name}",
            value = f"{amount}",
            inline = False
        )
        if index == x:
          break
        else:
          index += 1
        

    await ctx.send(embed=embed)


client.run(os.getenv("TOKEN"))

#End Of Code!