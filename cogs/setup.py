import discord
from discord.ext import commands
from discord import app_commands

class SetUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        @bot.event
        async def on_raw_reaction_add(self, payload):
            if payload.author.bot:
                return
            SetUp.give_role(payload)

        @bot.event
        async def on_raw_reaction_remove(self, payload):
            if payload.author.bot:
                return
            SetUp.remove_role(payload)
       
        with open("storage/reaction_roles.json", "r") as file:
            try:
                self.reaction_roles = json.load(file)
            except :
                self.reaction_roles = {}

    @app_commands.command(name="role_interactions", description="add role interactions to a message")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_interactions(self, interaction: discord.Interaction, message_id: str, emoji_role_pair:str):
        arg = emoji_role_pair.split()
        if len(arg)!= 2:
            await interaction.response.send_error("Invalid format. Use: ':emoji: role_name' multiple times in a row.", ephemeral=True)
            return
        try :
            message = await interaction.channel.fetch_message(int(message_id))
        except discord.NotFound:
            await interaction.response.send_error("Message not found.", ephemeral=True)
            return
        emoji_role_pairs = {}
        for i in range(0, len(arg), 2):
            emoji = arg[i]
            role_id = arg[i+1]
            role = interaction.guild.get_role(int(role_id))
            if role is None:
                await interaction.response.send_error(f"Role with id {role_id} not found.", ephemeral=True)
                return
            emoji_role_pairs[emoji] = role
            await message.add_reaction(emoji)
        self.reaction_roles[message_id] = emoji_role_pairs
        save_reaction_roles()

        await interaction.response.send_message("successfully set up role interactions for message {message_id}.", ephemeral=True)
        
    def give_role(self, payload):
        message_id = str(payload.message_id)
        if message_id in self.reaction_roles:
            emoji_role_pairs = self.reaction_roles[message_id]
            for emoji, role in emoji_role_pairs.items():
                if emoji in payload.emoji.name:
                    payload.member.add_roles(role)
                    return

    def remove_role(self, payload):
        message_id = str(payload.message_id)
        if message_id in self.reaction_roles:
            emoji_role_pairs = self.reaction_roles[message_id]
            for emoji, role in emoji_role_pairs.items():
                if emoji in payload.emoji.name:
                    payload.member.remove_roles(role)
                    return
    


def save_reaction_roles():
    with open("storage/reaction_roles.json", "w") as file:
        json.dump(reaction_roles, file)

async def setup(bot):
    await bot.add_cog(SetUp(bot))