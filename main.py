import discord
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
import os

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
    try:
        synced = await bot.tree.sync()  # Sync commands with Discord
        print(f'Successfully synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

# slash command: /ping
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


def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
load_cogs()


# Run the bot
bot.run(TOKEN)
