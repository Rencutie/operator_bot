import discord
from discord import app_commands
from discord.ext import commands
import os

# Load your bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True

# Create the bot object
bot = commands.Bot(command_prefix='!', intents=intents)

# Create a tree object for slash commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    try:
        synced = await bot.tree.sync()  # Sync commands with Discord
        print(f'Successfully synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

# Example slash command: /ping
@bot.tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.event
async def on_message(message):
    """
        get userID
        call loadData
        call checkUserLastText
        if true, call addExp
        check if he level up and call level up text

        does not return 
    """
    if message.author.bot:
        return
    TODO

async def loadData(userID):
    """
        open json and return disctionary
        if user not inside, return a call of createUser
    """
    TODO

async def createUser(userID):
    """
        make a new json object 
        level 0, 0 exp, username
        return dictionary of its data
    """
    
    TODO

async def checkUserLastText(userID):
    """
        check the last time the
        user got exp added and
        return true if it's more than 60s ago
    """
    TODO

async def addExp(userID):
    """
        add a random number between 7 and 13 to the
        users exp 
    """
    TODO

async def levelUpMessage(userData):
    """
        send a pretty message with the level archived and username
        userData : dictionary
    """
    TODO

@bot.command
async def level(ctx):
    # userID = [TODO]
    # userData = loadData
    # message with current lvl and exp
    pass



# Run the bot
bot.run(TOKEN)
