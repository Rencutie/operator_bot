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
    async def slash_ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('Pong!')
    
    @app_commands.command(name="help", description="show this message")
    async def slash_help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Help", description="List of available commands", color=discord.Color.blue())
        #set the bot's avatar as the embed's thumbnail
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        for cmd in self.bot.tree.walk_commands():
            embed.add_field(name=f"**/{cmd.name}**", value=f"__{cmd.description}__", inline=False)

        await interaction.response.send_message(embed=embed)



async def setup(bot):
    await bot.add_cog(General(bot))