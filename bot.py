# This example requires the 'members' and 'message_content' privileged intents to function.

import discord
import json
from discord.ext import commands
import random
import requests

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='uwu ',
                   description=description,
                   intents=intents)

with open("tokens.json") as f:
  bot_token = json.load(f)['token']
 
api_key = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'

@bot.event
async def on_ready():
  print(f'Logged in as {bot.user} (ID: {bot.user.id})')
  print('------')


@bot.command()
async def add(ctx, left: int, right: int):
  """Adds two numbers together."""
  await ctx.send(f"context: {ctx}")

  await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
  """Rolls a dice in NdN format."""
  try:
    rolls, limit = map(int, dice.split('d'))
  except Exception:
    await ctx.send('Format has to be in NdN!')
    return

  result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
  await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
  """Chooses between multiple choices."""
  await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
  """Repeats a message multiple times."""
  for i in range(times):
    await ctx.send(content)


@bot.command()
async def joined(ctx, member: discord.Member):
  """Says when a member joined."""
  await ctx.send(
    f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')


@bot.group()
async def cool(ctx):
  """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
  if ctx.invoked_subcommand is None:
    await ctx.send(f'No, {ctx.subcommand_passed} is not cool')


@cool.command(name='bot')
async def _bot(ctx):
  """Is the bot cool?"""
  await ctx.send('Yes, the bot is cool.')


#################################################################################################


@bot.command()
async def test(ctx, champ: str):
  """Says what role the champion is usually played"""
  try:
    if (champ == "Teemo"):
      await ctx.send("Top")
    else:
      raise ValueError("bad")
  except Exception:
    await ctx.send('Has to be league of legends champion name')
    return

@bot.command()
async def leagues(ctx, region: str):
  """Says what role the champion is usually played"""
  try:
    header = {'x-api-key': api_key,'hl': region}
    
    leagues = requests.get('https://prod-relapi.ewp.gg/persisted/gw/getLeagues',\
                 headers=header).json()['data']['leagues']

    league_names = [league['name'] for league in leagues]
    await ctx.send(league_names)

  except Exception as e:
    await ctx.send(e)
    return



bot.run(bot_token)
