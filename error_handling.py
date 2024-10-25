import discord
from discord.ext import commands
from discord import app_commands

async def handle_command_not_found(ctx, error):
    """Handle command not found error for traditional commands."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Never heard of that shit go kill yourself.")

async def handle_member_not_found(ctx, error):
    """Handle member not found error for traditional commands."""
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Please mention a user")

async def handle_missing_permissions(ctx, error):
    """Handle missing permissions error for traditional commands."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to execute this command.")


async def handle_missing_arg(ctx, error):
    """Handle missing argument error for traditional commands."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"missing argument : '{error.param.name}'")
