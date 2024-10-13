import discord
from discord import app_commands
from discord.ext import commands
import os

# local imports
import level

# Load your bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the bot
intents = discord.Intents.all()
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
    if message.author.bot:
        return

    userID = str(message.author.id)  # Convert userID to string
    username = message.author.name
    await level.onLevel(message, userID, username)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def lvl(ctx):
    userID = str(ctx.author.id)
    dataDict = level.loadData()
    print('uwu')
    await ctx.send(f"{ctx.author.name}, your current level is {dataDict[userID]['level']}\n Your current exp is {dataDict[userID]['exp']} out of {level.xp_requirements[dataDict[userID]['level']]} required to level up.")

# Run the bot
bot.run(TOKEN)
