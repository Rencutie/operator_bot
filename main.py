import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Define the bot with a command prefix (e.g., ! or ?)
intents = discord.Intents.all()  # Or use Intents.all() for more permissions
bot = commands.Bot(command_prefix='!', intents=intents)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# respond with "pong" to a "!ping" message
@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(TOKEN)
