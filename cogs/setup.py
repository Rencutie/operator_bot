import discord
from discord.ext import commands
from discord import app_commands
import json
class SetUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("storage/reaction_roles.json", "r") as file:
            try:
                self.reaction_roles = json.load(file)
            except :
                self.reaction_roles = {}


    @commands.Cog.listener() 
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:  # Ignore bot's own reactions
            return
        await self.give_role(payload)

    @commands.Cog.listener() 
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:  # Ignore bot's own reactions
            return
        await self.remove_role(payload)


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
        save_reaction_roles(self.reaction_roles)  # Save role IDs instead of Role objects

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
                        if role:  # Ensure role exists
                            await member.add_roles(role)
                            print(f"Added role {role.name} to {member.name}.")

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
                            print(f"Removed role {role.name} from {member.name}.")

    


def save_reaction_roles(reaction_roles):
    print(f"Saving reaction roles: {reaction_roles}")  # Debugging purposes
    with open("storage/reaction_roles.json", "w") as file:
        json.dump(reaction_roles, file)

async def setup(bot):
    await bot.add_cog(SetUp(bot))