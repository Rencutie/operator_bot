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
        """
        Very simple, will ban the given user
        USAGE: /ban MEMBER REASON(string)
        """
        await member.ban(reason=reason)
        await send_log(self.bot, f"{interaction.user.name} banned {member.name} for {reason}", self.log_channel_id)
        await interaction.response.send_message(f"{member.name} has been banned for the folowing reason: \n__{reason}__")
    


    @app_commands.command(name="kick", description="self explanatory")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """
        Kicks the given user out of the server.
        USAGE : /kick MEMBER REASON(string)
        """

        await member.kick(reason=reason)
        await send_log(self.bot, f"{interaction.user.name} kicked {member.name} for {reason}", self.log_channel_id)
        await interaction.response.send_message(f"{member.name} has been kicked for the following reason: \n__{reason}__")
    

    @app_commands.command(name="kill", description="send a user to the graveyard (moderators only)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_mute(self, interaction: discord.Interaction, member: discord.Member, reason: str, duration_min: str = "5" ):
        """
        This command will "kill" a user. the user will be given the role "ded" (assumed to exist). 
        The point is to give restricted access to people with this role for a said amount of time.
        USAGE : /kill MEMBER [duration_min]
        duration_min must be greater than 0
        """
        if not duration_min.isdigit():
            await interaction.response.send_message("Please provide a valid duration in minutes.", ephemeral=True)
            return
        
        duration = int(duration_min) * 60 #in seconds
        if duration<=0 :
            await interaction.response.send_message("Time must be strictly positive")
            return
        try: 
            await member.add_roles(discord.utils.get(self.bot.guilds[0].roles, name="ded"))
            await send_log(self.bot, f"{interaction.user.name} have killed {member.name} for {duration // 60} minutes", self.log_channel_id)
            await interaction.response.send_message(f"{member.name} has been sent to the graveyard for the following reason: \n__{reason}__\nThey shall resurrect in {duration // 60} minutes.")

            await asyncio.sleep(duration)
            await member.remove_roles(discord.utils.get(self.bot.guilds[0].roles, name="ded"))
            await send_log(self.bot, f"{member.name}'s sentence to the grave has ended.", self.log_channel_id)
        except Exception :
            send_log(self.bot, "The 'ded' role is required in the server to use this command.\nWe recomend to restrict access to most of the server for this role for this command to make sense.",self.log_channel_id)
    

    @app_commands.command(name="purge", description="delete messages (moderators only)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_purge(self, interaction: discord.Interaction, count: int):
        """
        Deleted the last given amount of message in the current channel.
        USAGE : /purge COUNT
        COUNT must be between 1 and 100
        """
        if count < 1 or count > 100:
            await interaction.response.send_message("Please provide a valid count between 1 and 100.", ephemeral=True)
            return

        try :
            await interaction.channel.purge(limit=count)
            await interaction.response.send_message("ok", ephemeral=True)
            await send_log(self.bot, f"{interaction.user.name} purged {count} messages in {interaction.channel.name}", self.log_channel_id)
        except :
            await interaction.response.send_message("you can do that here", ephemeral=True)
        


    @app_commands.command(name="resurect", description="send a user back from the graveyard (moderators only)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_resurrect(self, interaction: discord.Interaction, member: discord.Member):
        """
        Will remove the role "ded" (assumed to exist) to the given user. 
        USAGE: /resurect USER
        """

        if not discord.utils.get(member.roles, name="ded"):
            await interaction.response.send_message(f"{member.name} is not in the graveyard.", ephemeral=True)
            return
        await member.remove_roles(discord.utils.get(self.bot.guilds[0].roles, name="ded"))
        await send_log(self.bot, f"{interaction.user.name} have resurrected {member.name}", self.log_channel_id)
        await interaction.response.send_message(f"{member.name} has been resurrected from the graveyard.", ephemeral=True)
        

        
async def setup(bot):
    await bot.add_cog(Moderation(bot))
