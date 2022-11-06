# This example requires the 'members' and 'message_content' privileged intents to function.

import discord
import json
from discord.ext import commands
import datetime
import random
import requests
import time

description = '''This bot acts as an interactive live database for pro league of legends
tournaments and matches'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='LOL ',
                   description=description,
                   intents=intents)

with open("tokens.json") as f:
  bot_token = json.load(f)['token']
 
api_key = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'

@bot.event
async def on_ready():
  print(f'Logged in as {bot.user} (ID: {bot.user.id})')
  print('------')

def get_latest_date():
    now = datetime.datetime.now(datetime.timezone.utc)
    now = now - datetime.timedelta(
        seconds=now.second + 60,
        microseconds=now.microsecond
    )
    now_string = now.isoformat()
    return str(now_string).replace('+00:00', 'Z')

@bot.command()
async def leagues(ctx, region: str):
  """Lists all leagues in a region"""
  try:
    header = {'x-api-key': api_key,'hl': region}
    
    leagues = requests.get('https://prod-relapi.ewp.gg/persisted/gw/getLeagues',\
                 headers=header).json()['data']['leagues']

    league_names = [league['name'] for league in leagues]
    await ctx.send(league_names)

  except Exception as e:
    await ctx.send(e)
    return

@bot.command()
async def getSchedule(ctx, block, region='en-US'):
  """Lists all matches in a tourney"""
  try:
    header = {'x-api-key': api_key,'hl': region}

    block = block.capitalize()
    
    leagues = requests.get('https://prod-relapi.ewp.gg/persisted/gw/getLeagues',\
                 headers=header).json()['data']['leagues']
    leagueId = leagues[0]['id']
    leagueName = leagues[0]['name']
    
    output = f"Tournament Name: {leagueName}\nTournament ID: {leagueId}\n" + \
              "-------------------------------------------------"
    await ctx.send(output)


    header = {'x-api-key': api_key,'hl': region, 'leagueId': leagueId}
    schedule = requests.get('https://prod-relapi.ewp.gg/persisted/gw/getSchedule', \
                headers=header).json()

    found = False
    
    events = schedule['data']['schedule']['events']
   
    for event in events:
        if event['blockName'] == block:
          time_ = time.strptime(event['startTime'], '%Y-%m-%dT%H:%M:%SZ')
          time_ = datetime.datetime(*time_[:6])
          time_ = time_.strftime("%d-%B")
          matchID = event['match']['id']
          team1 = event['match']['teams'][0]['name']
          team2 = event['match']['teams'][1]['name']
          
          output = f"Time of Match: {time_}\nMatch: {team1} vs {team2}\nMatchID: {matchID}" + \
                    "\n-------------------------------------------------"
          found = True
          
          await ctx.send(output)


    if(found == False) :
      raise Exception("Arguments must be: 'Groups', 'Quarterfinals', 'Semifinals', 'Finals'")

  except Exception as e:
    await ctx.send(e)
    return
    


@bot.command()
async def getEventDetails(ctx, matchId, region='en-US'):
  """Lists all the games in a match. To find matchID, use getSchedule"""
  try:
    header = {'x-api-key': api_key, 'hl': region, 'id': str(matchId)}

    event = requests.get('https://prod-relapi.ewp.gg/persisted/gw/getEventDetails',\
                          headers=header).json()
                      

    games = event['data']['event']['match']['games']
    team1 = event['data']['event']['match']['teams'][0]['name']
    team2 = event['data']['event']['match']['teams'][1]['name']
    result1 = event['data']['event']['match']['teams'][0]['result']['gameWins']
    result2 = event['data']['event']['match']['teams'][1]['result']['gameWins']    

    await ctx.send("Event Results: ")
        
    await ctx.send(str(team1) + ": " + str(result1) + " vs. " + str(team2) + ": " + str(result2))


    for game in games :
      cnt = game['number']
      id_ = game['id']
      
      await ctx.send("Game " + str(cnt))
      await ctx.send("Game ID: " + str(id_))

  except Exception as e:
    await ctx.send(e)
    return
    
@bot.command()
async def getDetails(ctx, gameId):
  """"Get the full details of a game. To find gameID, use getEventDetails"""
  try:
    header = {'startingTime': f'{get_latest_date()}'}
    
    session = requests.Session()
    
    starting_time = get_latest_date() 
    frames = json.loads(session.get(
            f'https://feed.lolesports.com/livestats/v1/details/{str(gameId)}',
            params={
                'startingTime': starting_time,
            }
        ).text)['frames']
        
        
    gameWindow = json.loads(session.get(
            f'https://feed.lolesports.com/livestats/v1/window/{str(gameId)}',
            params={
                'startingTime': starting_time,
            }
        ).text)
        
    gameMetadata = gameWindow['gameMetadata'] 
    gameState = gameWindow['frames'][-1]
    
        
    participants = gameMetadata['blueTeamMetadata']['participantMetadata'] + \
                   gameMetadata['redTeamMetadata']['participantMetadata']
    
    participantDict = {}
    for participant in participants:
        participantDict[participant['participantId']] = {'summonerName': participant['summonerName'],\
                        'champion': participant['championId'], 'role': participant['role']}
            
            
    
    players = [participantDict[participant['participantId']] for participant in frames[-1]['participants']]
    cs = [participant['creepScore'] for participant in frames[-1]['participants']]
                 
    
    team1 = participantDict[1]['summonerName'].split(' ')[0]
    team2 = participantDict[10]['summonerName'].split(' ')[0]

    out = f"{team1} vs {team2}\n"
    out += f"State: {gameState['gameState'].replace('_', ' ').capitalize()}\nTotal Kills: {gameState['blueTeam']['totalKills']} to {gameState['redTeam']['totalKills']}"
    out += f"\nTotal Gold: {gameState['blueTeam']['totalGold']} to {gameState['redTeam']['totalGold']}"
    
    out += "\n-------------------------------------------------"
    await ctx.send(out)

    for idx, player in enumerate(participantDict.keys()):
        player_metadata = participantDict[player]
        player_stats = frames[-1]['participants'][idx]
        out = f"Player: {player_metadata['summonerName']},\nRole: {player_metadata['role']}\nChampion: {player_metadata['champion']}\n"
        out += f"K/D/A: {player_stats['kills']}/{player_stats['deaths']}/{player_stats['assists']}"
        out += f"\nCS: {player_stats['creepScore']}\nGold: {player_stats['totalGoldEarned']}"
        out += '\n-------------------------------------------------'
        await ctx.send(out)
       

    
  except Exception as e:
    await ctx.send(e)
    return


bot.run(bot_token)
