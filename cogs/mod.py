import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio

from error_handling import send_log

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("storage/config.json", "r") as file:
            self.config = json.load(file)
        self.log_channel_id = self.config.get("channel", {}).get("log_channel_id", -1)
    

    @app_commands.command(name="ban", description="self explanatory")
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_ban(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        await member.ban(reason=reason)
        await send_log(self.bot, f"{interaction.user.name} banned {member.name} for {reason}", self.log_channel_id)
        await interaction.response.send_message(f"{member.name} has been banned for the folowing reason: \n__{reason}__")
    


    @app_commands.command(name="kick", description="self explanatory")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        await member.kick(reason=reason)
        await send_log(self.bot, f"{interaction.user.name} kicked {member.name} for {reason}", self.log_channel_id)
        await interaction.response.send_message(f"{member.name} has been kicked for the following reason: \n__{reason}__")
    

    @app_commands.command(name="kill", description="send a user to the graveyard (moderators only)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_mute(self, interaction: discord.Interaction, member: discord.Member, reason: str, duration_min: str = "5" ):
        if not duration_min.isdigit():
            await interaction.response.send_message("Please provide a valid duration in minutes.", ephemeral=True)
            return
        duration = int(duration_min) * 60 #in seconds
        
        await member.add_roles(discord.utils.get(self.bot.guilds[0].roles, name="Dead"))
        await send_log(self.bot, f"{interaction.user.name} have killed {member.name} for {duration // 60} minutes", self.log_channel_id)
        await interaction.response.send_message(f"{member.name} has been sent to the graveyard for the following reason: \n__{reason}__\nThey shall resurrect in {duration // 60} minutes.")

        await asyncio.sleep(duration)
        await member.remove_roles(discord.utils.get(self.bot.guilds[0].roles, name="Dead"))
        await send_log(self.bot, f"{member.name}'s sentence to the grave has ended.", self.log_channel_id)
    

    @app_commands.command(name="purge", description="delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_purge(self, interaction: discord.Interaction, count: int):
        if count < 1 or count > 100:
            await interaction.response.send_message("Please provide a valid count between 1 and 100.", ephemeral=True)
            return
        await interaction.response.send_message("ok", ephemeral=True)
        await interaction.channel.purge(limit=count)
        await send_log(self.bot, f"{interaction.user.name} purged {count} messages in {interaction.channel.name}", self.log_channel_id)

    @app_commands.command(name="resurect", description="send a user back from the graveyard (moderators only)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_resurrect(self, interaction: discord.Interaction, member: discord.Member):
        if not discord.utils.get(member.roles, name="Dead"):
            await interaction.response.send_message(f"{member.name} is not in the graveyard.", ephemeral=True)
        await member.remove_roles(discord.utils.get(self.bot.guilds[0].roles, name="Dead"))
        await send_log(self.bot, f"{interaction.user.name} have resurrected {member.name}", self.log_channel_id)
        await interaction.response.send_message(f"{member.name} has been resurrected from the graveyard.", ephemeral=True)
        

        
async def setup(bot):
    await bot.add_cog(Moderation(bot))