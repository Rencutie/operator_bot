import discord
from dotenv import load_dotenv
from discord.ext import commands
import os
import json
import sys

# local imports
import level
from error_handling import send_log

load_dotenv()

# Load your bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
print("--------------------------------", file=sys.stderr)
print("starting bot. . .", file=sys.stderr)
print("--------------------------------", file=sys.stderr)
# Set up the bot
intents = discord.Intents.all()
intents.message_content = True

# Create the bot object
bot = commands.Bot(command_prefix='!', intents=intents)

with open('storage/config.json', 'r') as f:
    config = json.load(f)
log_channel_id = config.get('channel').get('log_channel_id')

# for slash commands
@bot.event
async def on_ready():
    print("--------------------------------", file=sys.stderr)
    print(f"Logged in as {bot.user.name}", file=sys.stderr)
    print("--------------------------------", file=sys.stderr)
    await send_log(bot, 'Bot started', log_channel_id)
    await load_cogs()
    try:
        synced = await bot.tree.sync()  # Sync commands with Discord
        await send_log(bot,f'Successfully synced {len(synced)} commands', log_channel_id)
        print(f"Synced {len(synced)} commands", file=sys.stderr)

    except Exception as e:
        await send_log(bot, f'Error syncing commands: {e}', log_channel_id)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    userID = str(message.author.id) 
    username = message.author.name
    await level.onLevel(message, userID, username)
    await bot.process_commands(message)

    


async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


# Run the bot
bot.run(TOKEN)
