import discord
from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @app_commands.command(name="ping", description="check if the bot is on")
    async def slash_ping(self, ctx):
        await interaction.response.send_message('Pong!')



async def setup(bot):
    await bot.add_cog(General(bot))