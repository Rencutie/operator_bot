import discord
from discord.ext import commands
from discord import app_commands
from level import loadData, xp_requirements

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
            embed.add_field(name=f"**/{cmd.name}**", value=f"> {cmd.description}", inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1299461270914863125/1304133666309541971/bannerBot.jpg?ex=672e489f&is=672cf71f&hm=ec5c4a6a232c6f3c73691c217cbf736cb3ba52cd83281d6af72fc96918d1d103&") #banner
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="profile", description="show a user's profile")
    async def slash_profile(self, interaction: discord.Interaction, member: discord.Member = None):
        if member == None:
            member = interaction.user
        embed = discord.Embed(title=f"{member.name}'s Profile", description=f"Created: {member.created_at.strftime('%d/%m/%Y')}", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        dataDict = loadData()
        if str(member.id) in dataDict:
            exp = dataDict[str(member.id)]['exp']
            Level = dataDict[str(member.id)]['level']
        else:
            exp = 0
            Level = 1
        embed.add_field(name="level : ", value=Level)
        embed.add_field(name="experience: ", value=f"{exp} / {xp_requirements[Level]}")
        embed.add_field(name="joind at : ", value=f"{member.joined_at.strftime("%B %d, %Y")}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))