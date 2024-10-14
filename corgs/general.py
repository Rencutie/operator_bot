import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.slash_command(name="ping", description="check if the bot is on")
    async def slash_ping(self, ctx):
        await ctx.send('Pong!')



def setup(bot):
    bot.add_cog(General(bot))
