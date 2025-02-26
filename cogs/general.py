import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
import xml.etree.ElementTree as ET

from discord.webhook.async_ import interaction_response_params
from level import loadData, xp_requirements

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_pages = []
    general_group = app_commands.Group(name="general", description="some all and nothing commands")

    @general_group.command(name="ping", description="check if the bot is on")
    async def slash_ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('Pong!')
    
    def generate_help_pages(self):
        """Generates help pages based on command groups."""
        self.help_pages.clear()
        
        def process_group(group, parent_name=""):
            full_name = f"{parent_name} {group.name}".strip()
            description = f"**/{full_name}** - {group.description}\n\n"
            for subcommand in group.commands:
                if isinstance(subcommand, app_commands.Group):
                    process_group(subcommand, full_name)
                else:
                    description += f"**/{full_name} {subcommand.name}** - {subcommand.description}\n"
            self.help_pages.append((full_name, description))
        
        for command in self.bot.tree.get_commands():
            if isinstance(command, app_commands.Group):
                process_group(command)
            else:
                self.help_pages.append((command.name, f"**/{command.name}** - {command.description}"))
    
    @general_group.command(name="help", description="Shows help for command groups.")
    async def slash_help(self, interaction: discord.Interaction):
        self.generate_help_pages()
        if not self.help_pages:
            await interaction.response.send_message("No command groups available.", ephemeral=True)
            return
        
        current_page = 0
        embed = self.create_embed(current_page)
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        
        def check(reaction, user):
            return user == interaction.user and reaction.message.id == message.id and reaction.emoji in ["⬅️", "➡️"]
        
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction.emoji, user)
                
                if reaction.emoji == "➡️":
                    current_page = (current_page + 1) % len(self.help_pages)
                elif reaction.emoji == "⬅️":
                    current_page = (current_page - 1) % len(self.help_pages)
                
                await message.edit(embed=self.create_embed(current_page))
            except TimeoutError:
                break
    
    def create_embed(self, page_index):
        group_name, description = self.help_pages[page_index]
        embed = discord.Embed(title=f"Help - {group_name}", description=description, color=discord.Color.blue())
        embed.set_footer(text=f"Page {page_index + 1}/{len(self.help_pages)}")
        return embed

    @general_group.command(name="profile", description="show a user's profile")
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

    
    @general_group.command(name="rule34", description="send a random rule34 image or video", nsfw=True)
    async def slash_rule34(self, interaction: discord.Interaction, tags: str): 
        base_url = "https://api.rule34.xxx/index.php"

        # Clean up tags and replace spaces with "+"
        formatted_tags = " ".join(tags.split()).replace(" ", "+")  
        params = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "tags": formatted_tags,  
            "limit": 100
        }

        # Manually build the query string
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        final_url = f"{base_url}?{query_string}"
       
        async with aiohttp.ClientSession() as session:
            async with session.get(final_url) as response:  # Use final_url directly
                if response.status != 200:
                    await interaction.response.send_message("rule34 unreachable")
                    return
                xml_data = await response.text()
                root = ET.fromstring(xml_data)
                post_count = int(root.attrib.get("count", 0))
                page_count = int(post_count / 100)

                # Adjust params for pagination
                params = {
                    "page": "dapi",
                    "s": "post",
                    "q": "index",
                    "tags": formatted_tags,
                    "limit": 100,
                    "pid": random.randint(0, page_count)
                }

                # Build the new query string for pagination
                query_string = "&".join([f"{key}={value}" for key, value in params.items()])
                final_url = f"{base_url}?{query_string}"
                
            async with session.get(final_url) as response:  # Use final_url for the second request
                if response.status != 200:
                    await interaction.response.send_message("rule34 unreachable")
                    return
                xml_data = await response.text()
                root = ET.fromstring(xml_data)
                posts = root.findall("post")
                if not posts:
                    await interaction.response.send_message("no results matching these tags")
                    return

                random_post = random.choice(posts)
                image_url = random_post.attrib.get("file_url")

                if image_url:
                    await interaction.response.send_message(image_url)
                else:
                    await interaction.response.send_message("weird error of selected post not having a url")
async def setup(bot):
    await bot.add_cog(General(bot))
