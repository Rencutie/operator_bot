import discord
from discord.ext import commands
from discord import app_commands
import level
from error_handling import *

class LvlCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="lvl")
    async def lvl(self, ctx, member: discord.Member = None):
        if member == None :
            member = ctx.author
        userID = str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await ctx.send(f"{member.mention} is not in the database.\nPrehaps they never sent a message")
            return
        current_lvl = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp']
        await ctx.send(f"{member.name}, your current level is {dataDict[userID]['level']}\nYour current exp is {dataDict[userID]['exp']} out of {level.xp_requirements[dataDict[userID]['level']]} required to level up.")



    @app_commands.command(name ="lvl", description="show a user's level. Show self if no user is given")
    async def slash_lvl(self, interaction:discord.Interaction, member: discord.Member = None):
        if member == None :
            member = interaction.user
        userID = str(member.id)
        dataDict = level.loadData()
        
        if userID not in dataDict:
            await interaction.response.send_message(f"{member.mention} is not in the database.\nPrehaps they have never sent a message")
            return

        await interaction.response.send_message(f"{member.name}, your current level is {dataDict[userID]['level']}\nYour current exp is {dataDict[userID]['exp']} out of {level.xp_requirements[dataDict[userID]['level']]} required to level up.")

    

    @commands.command(name="addexp")
    @commands.has_permissions(administrator=True)
    async def addExp(self, ctx, member: discord.Member, amount:int = -1):
        if member == None:
            await ctx.send("You need to specify a member to add experience points to.")
            return
        if amount < 1:
            await ctx.send("You need to specify a positive amount of experience points to add.")
            return
        userID = str(member.id)
        dataDict = level.loadData()

        if userID not in dataDict:
            await ctx.send(f"{member.mention} does not exist in the database. Creating a new entry.")
            level.createUser(dataDict, userID, member.name)

        current_level, current_exp = self.add_exp_logic(dataDict, userID, amount)
        level.saveData(dataDict)
        await ctx.send(f"Added {amount} EXP to {member.mention}.\nNew Level: {current_level}\nNew EXP: {current_exp}")

    # Slash command version of adding experience points
    @app_commands.command(name="addexp", description="Add experience points to a user. (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_addExp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if member == None:
            await interaction.response.send_message("You need to specify a member to add experience points to.", ephemeral=True)
            return
        if amount < 1:
            await interaction.response.send_message("You need to specify a positive amount of experience points to add.", ephemeral=True)
            return
        userID = str(member.id)
        dataDict = level.loadData()

        if userID not in dataDict:
            await send_log(self.bot, f"{interaction.user.name} tried to add exp to {member.name} but {member.name} does not exist in the database. Creating a new entry.")
            await interaction.response.send_message(f"{member.mention} does not exist in the database. Creating a new entry.")
            level.createUser(dataDict, userID, member.name)

        current_level, current_exp = self.add_exp_logic(dataDict, userID, amount)
        level.saveData(dataDict)
        await send_log(self.bot, f"{interaction.user.name} added {amount} exp to {member.name}. New Level: {current_level}, New EXP: {current_exp}")
        await interaction.response.send_message(f"Added {amount} EXP to {member.mention}.\nNew Level: {current_level}\nNew EXP: {current_exp}")

    def add_exp_logic(self, dataDict, userID, amount):
        current_level = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp'] + amount
        try:
            treshold = level.xp_requirements[current_level]
        except KeyError:
            dataDict[userID]['exp'] = current_exp
            return current_level, current_exp+amount
        while current_exp >= treshold:
            current_level += 1
            current_exp -= treshold
            if current_level >= 100:
                break # if max level reached, break loop
            treshold = level.xp_requirements[current_level]

        dataDict[userID]['level'] = current_level
        dataDict[userID]['exp'] = current_exp

        return current_level, current_exp


    @commands.command(name="setlevel")
    @commands.has_permissions(administrator=True)
    async def setLvl(self, ctx, member: discord.Member, lvl:int):
        if lvl < 1:
            await ctx.send("Cannot set level below 1.")
            return
        if lvl > 100:
            await ctx.send("Cannot set level above 100.")
            return
        userID= str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await ctx.send (f"{member.mention} does not exist in the database, creating {member.mention}")
            level.createUser(dataDict, userID, member.name)
        initLvl = dataDict[userID]['level']
        dataDict[userID]['level'] = lvl
        dataDict[userID]['exp'] = 0
        level.saveData(dataDict)
        await ctx.send(f"Set {member.mention} level to {lvl}; experiance set to 0\nWas level {initLvl}")


    @app_commands.command(name="setlvl", description="set a user's level to a given number (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setLvl(self, interaction:discord.Interaction, member: discord.Member, lvl:int):
        if lvl < 1:
            await interaction.response.send_message("Cannot set level below 1.", ephemeral=True)
            return
        if lvl > 100:
            await interaction.response.send_message("Cannot set level above 100.", ephemeral=True)
            return
        userID= str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await send_log(self.bot, f"{interaction.user.name} tried to set level to {member.name} but {member.name} does not exist in the database. Creating {member.mention}")
            await interaction.response.send_message(f"{member.mention} does not exist in the database, creating {member.mention}")
            level.createUser(dataDict, userID, member.name)

        initLvl = dataDict[userID]['level']
        dataDict[userID]['level'] = lvl
        dataDict[userID]['exp'] = 0
        level.saveData(dataDict)
        await send_log(self.bot, f"{interaction.user.name} set level to {member.name} to {lvl}; experiance set to 0")
        await interaction.response.send_message(f"Set {member.mention} level to {lvl}; experiance set to 0\nWas level {initLvl}")
    

    @commands.command(name="rmexp")
    @commands.has_permissions(administrator=True)
    async def rmExp(self, ctx, member: discord.Member, amount:int):
        if amount < 1:
            await ctx.send("Cannot remove less than 1 exp.")
            return
        userID = str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await ctx.send(f"{member.mention} does not exist in database, you cannot remove them exp as they have none.")
            return
        current_lvl, current_exp = self.rmExp_logic(dataDict, userID, amount)
        dataDict[userID]['level'] = current_lvl
        dataDict[userID]['exp'] = current_exp
        level.saveData(dataDict)
        await ctx.send(f"Removed experience points from {member.mention}. They are now at level {current_lvl} with {current_exp} exp.")

    
    @app_commands.command(name="removeexp", description="remove a said amount of exp to a user (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_rmExp(self, interaction:discord.Interaction, member:discord.Member, amount:int):
        if amount < 1:
            await interaction.response.send_message("Cannot remove less than 1 exp.")
            return
        userID = str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await send_log(self.bot, f"{interaction.user.name} tried to remove exp to {member.name} but {member.name} does not exist in the database.")
            await interaction.response.send_message(f"{member.mention} does not exist in database, you cannot remove them exp as they have none.")
            return
        current_lvl, current_exp = self.rmExp_logic(dataDict, userID, amount)
        
        dataDict[userID]['level'] = current_lvl
        dataDict[userID]['exp'] = current_exp
        level.saveData(dataDict)
        await send_log(self.bot, f"{interaction.user.name} removed {amount} exp to {member.name} ")
        await interaction.response.send_message(f"Removed experience points from {member.mention}. They are now at level {current_lvl} with {current_exp} exp.")


    def rmExp_logic(self, dataDict, userID, amount):
        current_lvl = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp']
        while amount > 0:
            if current_lvl == 1 and current_exp == 0:
                break
            if current_exp < amount:
                amount -= current_exp
                current_exp = 0
                if current_lvl > 1 :
                    current_lvl -= 1
                    current_exp = level.xp_requirements[current_lvl]
            else:
                current_exp -= amount
                amount = 0
        return current_lvl, current_exp

    # to be done in the future :

    # @app_commands.command(name="leaderboard", description="Shows the top 10 users with the highest levels")
    # async def slash_leaderboard(self, interaction: discord.Interaction):
    #     dataDict = level.loadData()
    #     sorted_data = sorted(dataDict.items(), key=lambda x: x[1]['level'], reverse=True)
    #     leaderboard = []
    #     for i, (userID, data) in enumerate(sorted_data[:10], start=1):
    #         member = await ctx.guild.fetch_member(int(userID))
    #         leaderboard.append(f"{i}. {member.display_name} - Level: {data['level']}")



    @lvl.error
    async def lvl_error(self, ctx, error):
        await handle_member_not_found(ctx, error)


    @addExp.error
    async def addExp_error(self, ctx, error):
        await handle_member_not_found(ctx, error)
        await handle_missing_permissions(ctx, error)
        await handle_missing_arg(ctx, error)


    @rmExp.error
    async def rmExp_error(self, ctx, error):
        await handle_member_not_found(ctx, error)
        await handle_missing_permissions(ctx, error)
        await handle_missing_arg(ctx, error)
    

    @setLvl.error
    async def setLvl_error(self, ctx, error):
        await handle_member_not_found(ctx, error)
        await handle_missing_permissions(ctx, error)
        await handle_missing_arg(ctx, error)
    
async def setup(bot):
    await bot.add_cog(LvlCmd(bot))