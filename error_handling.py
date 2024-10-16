import discord
from discord.ext import commands
from discord import app_commands

async def handle_member_not_found(ctx, error):
    """Handle member not found error for traditional commands."""
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("please mention a user")

async def handle_slash_member_not_found(interaction: discord.Interaction, error):
    """Handle member not found error for slash commands."""
    if isinstance(error, app_commands.CommandInvokeError) and isinstance(error.original, app_commands.MemberNotFound):
        await interaction.response.send_message("please mention a user")
