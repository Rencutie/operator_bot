import discord
from discord.ext import commands
from discord import app_commands
import json

from error_handling import send_log



class SetUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("storage/reaction_roles.json", "r") as file:
            try:
                self.reaction_roles = json.load(file)
            except :
                self.reaction_roles = {}
        with open("storage/config.json", "r") as file:
            try:
                self.config = json.load(file)
            except :
                print("Error loading config.json")
        self.log_channel_id = self.config.get("channel", {}).get("log_channel_id", -1)
        self.welcome_channel_id = self.config.get("channel", {}).get("welcome_channel_id", -1)
        self.byebye_channel_id = self.config.get("channel", {}).get("byebye_channel_id", -1)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        await self.give_role(payload)

    @commands.Cog.listener() 
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id: 
            return
        await self.remove_role(payload)

    @commands.Cog.listener() 
    async def on_member_join(self, member):
        await self.send_welcome_message(member, self.welcome_channel_id)

    @commands.Cog.listener()
    async def on_raw_member_leave(self, member):
        await self.send_byebye_message(member, self.byebye_channel_id)
    
    

    @app_commands.command(name="set_log_channel", description="Set the log channel (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel : discord.TextChannel):
        self.config["channel"]["log_channel_id"] = channel.id
        save_config(self.config, "storage/config.json")
        await send_log(self.bot, "Log channel set to: " + channel.mention, self.log_channel_id)
        await interaction.response.send_message("set log channel to" + channel.mention)


    @app_commands.command(name="set_welcome_channel", description="Set the welcome channel (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_channel(self, interaction: discord.Interaction, channel : discord.TextChannel):
        self.config["channel"]["welcome_channel_id"] = channel.id
        save_config(self.config, "storage/config.json")
        await send_log(self.bot, "Welcome channel set to: " + channel.mention, self.log_channel_id)
        await interaction.response.send_message("set welcome channel to" + channel.mention)


    @app_commands.command(name="set_byebye_channel", description="Set the byebye channel (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_byebye_channel(self, interaction: discord.Interaction, channel : discord.TextChannel):
        self.config["channel"]["byebye_channel_id"] = channel.id
        save_config(self.config, "storage/config.json")
        await send_log(self.bot, "Byebye channel set to: " + channel.mention, self.log_channel_id)
        await interaction.response.send_message("set byebye channel to" + channel.mention)


    @app_commands.command(name="role_interactions", description="Add role interactions to a message (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_interactions(self, interaction: discord.Interaction, message_id: str, *, emoji_role_pairs: str):
        pairs = emoji_role_pairs.split()

        if len(pairs) % 2 != 0:
            await interaction.response.send_message("Invalid format. Use: ':emoji: @role_name' multiple times in a row.", ephemeral=True)
            return

        try:
            message = await interaction.channel.fetch_message(int(message_id))
        except discord.NotFound:
            await interaction.response.send_message("Message not found.", ephemeral=True)
            return

        emoji_role_map = {}

        for i in range(0, len(pairs), 2):
            emoji = pairs[i]
            role_mention = pairs[i + 1]

            # Extract role ID from mention
            role = None
            if role_mention.startswith("<@&") and role_mention.endswith(">"):
                role_id = int(role_mention[3:-1])
                role = interaction.guild.get_role(role_id)

            if role is None:
                await interaction.response.send_message(f"Role '{role_mention}' not found.", ephemeral=True)
                return

            # Store the emoji and the role ID instead of the Role object
            emoji_role_map[emoji] = role.id

            await message.add_reaction(emoji)

        self.reaction_roles[message_id] = emoji_role_map
        save_config(self.reaction_roles, "storage/reaction_roles.json")  # Save role IDs instead of Role objects

        await interaction.response.send_message(f"Successfully set up role interactions for message {message_id}.", ephemeral=True)

    


    async def give_role(self, payload):
        message_id = str(payload.message_id)
        if message_id in self.reaction_roles:
            emoji_role_pairs = self.reaction_roles[message_id]
            for emoji, role_id in emoji_role_pairs.items():
                if emoji == payload.emoji.name:
                    guild = self.bot.get_guild(payload.guild_id)
                    member = guild.get_member(payload.user_id)
                    if member and role_id:
                        role = guild.get_role(role_id)  # Fetch the Role object
                        if role:  
                            await member.add_roles(role)
                            await send_log(self.bot, f"Added role {role.name} to {member.name}.", self.log_channel_id)

    async def remove_role(self, payload):
        message_id = str(payload.message_id)
        if message_id in self.reaction_roles:
            emoji_role_pairs = self.reaction_roles[message_id]
            for emoji, role_id in emoji_role_pairs.items():
                if emoji == payload.emoji.name:
                    guild = self.bot.get_guild(payload.guild_id)
                    member = guild.get_member(payload.user_id)
                    if member and role_id:
                        role = guild.get_role(role_id)  # Fetch the Role object
                        if role:  # Ensure role exists
                            await member.remove_roles(role)
                            await send_log(self.bot, f"Removed role {role.name} from {member.name}.", self.log_channel_id)


    async def send_welcome_message(self, member, channel_id):
        if channel_id == -1 :
            await send_log(self.bot, "welcome message not configured.", self.log_channel_id)
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await send_log(self.bot, "channel to send welcome message does not exist.", self.log_channel_id)
            return
        embed = discord.Embed(title=f"Welcome {member.name}", description=f"joined on {member.joined_at.strftime('%d/%m/%Y')}", color=discord.Color.green())
        embed.set_image(url=member.display_avatar.url)
        await channel.send(embed=embed)


    async def send_byebye_message(self, member, channel_id):
        if channel_id == -1 :
            await send_log("bye message not configured.", self.log_channel_id)
            return
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await send_log("channel to send bye messages does not exist.", self.log_channel_id)
            return
        embed = discord.Embed(title=f"we hope never to see you again {member.name}", description=f"joined on {member.joined_at.strftime('%d/%m/%Y')}", color=discord.Color.red())
        embed.set_image(url=member.display_avatar.url)
        await channel.send(embed=embed)

            


def save_config(dict, file_path: str):
    with open(file_path, "w") as file:
        json.dump(dict, file, indent=4)
        
async def setup(bot):
    await bot.add_cog(SetUp(bot))
