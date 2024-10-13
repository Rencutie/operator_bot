import discord
from discord import app_commands
from discord.ext import commands
import os

# local imports
import level

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
    if message.author.bot:
        return
    userID = message.author.id
    username = message.author.name
    level.onLevel(message, userID, username)


# Run the bot
bot.run(TOKEN)
