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

async def send_log(bot, message, channel_id):
    """
    Sends a log message to the log channel. 
    If log channel is not configured or is missing, sends the error to stdout.
    """
    if channel_id == -1 :
        print("missconfig log channel.")
        return
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("missconfig log channel (inexistante).")
        return
    await channel.send(message)
