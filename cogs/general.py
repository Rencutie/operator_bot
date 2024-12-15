import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
import xml.etree.ElementTree as ET
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
    async def slash_profile(self, interaction: discord.Interaction, member: discord.Member):
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
        embed.add_field(name="joind at : ", value=member.joined_at.strftime("%B %d, %Y"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rule34", description="send a random rule34 image or video")
    @commands.is_nsfw()
    async def slash_rule34(self, interaction: discord.Interaction, tags: str):
        base_url = "https://api.rule34.xxx/index.php"
        params = {
        "page": "dapi",
        "s": "post",
        "q": "index",
        "tags": tags.replace(" ", "+"),  # Replace spaces with +
        "limit": 100
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response != 200:
                    await interaction.response.send_message("rule34 unreachable")
                    return
                xml_data = await response.text()
                root = ET.fromstring(xml_data)
                post_count = int(root.attrib.get("count", 0))
                page_count = int(post_count/100)
                params = {
                "page": "dapi",
                "s": "post",
                "q": "index",
                "tags": tags.replace(" ", "+"),  # Replace spaces with +
                "limit": 100,
                "pid": random.randint(0,page_count)
                }
            async with session.get(base_url, params=params) as response:
                if response.status != 200:
                    await interaction.response.send_message("rule34 unreachable")
                    return
                xml_data = await response.text()
                root = ET.fromstring(xml_data)
                posts = root.findall("posts")
                if not posts:
                    await interaction.response.send_message("no results matching these tags")
                    return
                random_post = random.choice(posts) 
                image_url = random_post.attrib.get("file_url")

                if image_url :
                    await interaction.response.send_message(image_url)
                else:
                    await interaction.response.send_message("weird error of selected post not having a url")

async def setup(bot):
    await bot.add_cog(General(bot))
