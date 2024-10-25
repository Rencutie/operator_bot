import discord
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
import os
from cogs.setup import SetUp
# local imports
import level

load_dotenv()

# Load your bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the bot
intents = discord.Intents.all()
intents.message_content = True

# Create the bot object
bot = commands.Bot(command_prefix='!', intents=intents)

# for slash commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    await load_cogs()
    try:
        synced = await bot.tree.sync()  # Sync commands with Discord
        print(f'Successfully synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    userID = str(message.author.id) 
    username = message.author.name
    level.onLevel(message, userID, username)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.author.bot:
        return
    SetUp.give_role(payload)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.author.bot:
        return
    SetUp.remove_role(payload)
    
    


async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


# Run the bot
bot.run(TOKEN)
