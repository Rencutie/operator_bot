import discord
from discord.ext import commands
from discord import app_commands
import level
from error_handling import send_log 
import json

class LvlCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('storage/config.json', 'r') as f:
            self.config = json.load(f)
        self.log_channel_id = self.config["channel"]['log_channel_id']
    
    lvl_group = app_commands.Group(name="lvl", description="Commands related to levels")    

    @lvl_group.command(name ="lvl", description="show a given user's level.")
    async def slash_lvl(self, interaction:discord.Interaction, member: discord.Member):
        """
        Usage : /lvl MEMBER
        """
        userID = str(member.id)
        dataDict = level.loadData()
        
        if userID not in dataDict:
            await interaction.response.send_message(f"{member.mention} is not in the database.\nPrehaps they have never sent a message")
            return

        await interaction.response.send_message(f"{member.name}, your current level is {dataDict[userID]['level']}\nYour current exp is {dataDict[userID]['exp']} out of {level.xp_requirements[dataDict[userID]['level']]} required to level up.")

    



    # Slash command version of adding experience points
    @lvl_group.command(name="addexp", description="Add experience points to a user. (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_addExp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """
        Allow the user to add experience to a given user.
        Usage : /addexp MEMBER AMOUNT(int).
        AMOUNT must be greater than 0.
        TODO : check for float
        """
        if amount < 1:
            await interaction.response.send_message("You need to specify a positive amount of experience points to add.", ephemeral=True)
            return
        userID = str(member.id)
        dataDict = level.loadData()

        if userID not in dataDict:
            await send_log(self.bot, f"{interaction.user.name} tried to add exp to {member.name} but {member.name} does not exist in the database. Creating a new entry.", self.log_channel_id)
            level.createUser(dataDict, userID, member.name)

        current_level, current_exp = self.add_exp_logic(dataDict, userID, amount)
        level.saveData(dataDict)
        await send_log(self.bot, f"{interaction.user.name} added {amount} exp to {member.name}. New Level: {current_level}, New EXP: {current_exp}", self.log_channel_id)
        await interaction.response.send_message(f"Added {amount} EXP to {member.mention}.\nNew Level: {current_level}\nNew EXP: {current_exp}")

    def add_exp_logic(self, dataDict, userID, amount):
        """
        This fonction impelement the algorithm behind the addition of exp to ensure propoer leveling up.
        return: a tuple with the new level and the new exp. if the max level is reached, the exp will keep adding up.
        """
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




    @lvl_group.command(name="setlvl", description="set a user's level to a given number (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_setLvl(self, interaction:discord.Interaction, member: discord.Member, lvl:int):
        """
        Set a user's level to a given number.
        USAGE : /setlvl MEMBER LVL(int)
        LVL must be between 1 and 100
        """
        if lvl < 1:
            await interaction.response.send_message("Cannot set level below 1.", ephemeral=True)
            return
        if lvl > 100:
            await interaction.response.send_message("Cannot set level above 100.", ephemeral=True)
            return
        userID= str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await send_log(self.bot, f"{interaction.user.name} tried to set level to {member.name} but {member.name} does not exist in the database. Creating {member.mention}", self.log_channel_id)
            level.createUser(dataDict, userID, member.name)

        dataDict[userID]['level'] = lvl
        dataDict[userID]['exp'] = 0
        level.saveData(dataDict)
        await send_log(self.bot, f"{interaction.user.name} set level to {member.name} to {lvl}; experiance set to 0", self.log_channel_id )
        await interaction.response.send_message(f"{member.mention} did not exist in the database, created {member.mention} at level {lvl}")
    

    
    
    @lvl_group.command(name="removeexp", description="remove a said amount of exp to a user (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_rmExp(self, interaction:discord.Interaction, member:discord.Member, amount:int):
        """
        Remove a given amount of exp to a user.
        USAGE : /removeexp MEMBER AMOUNT(int)
        AMOUNT must be greater than 1 
        """
        if amount < 1:
            await interaction.response.send_message("Cannot remove less than 1 exp.")
            return
        userID = str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await send_log(self.bot, f"{interaction.user.name} tried to remove exp to {member.name} but {member.name} does not exist in the database.", self.log_channel_id)
            await interaction.response.send_message(f"{member.mention} does not exist in database, you cannot remove them exp as they have none.")
            return
        current_lvl, current_exp = self.rmExp_logic(dataDict, userID, amount)
        
        dataDict[userID]['level'] = current_lvl
        dataDict[userID]['exp'] = current_exp
        level.saveData(dataDict)
        await send_log(self.bot, f"{interaction.user.name} removed {amount} exp to {member.name} ", self.log_channel_id)
        await interaction.response.send_message(f"Removed experience points from {member.mention}. They are now at level {current_lvl} with {current_exp} exp.")


    def rmExp_logic(self, dataDict, userID, amount):
        """
        This algorithm takes care to safely remove the exp to a user, as well as decrementing his level.
        Will return a tuple with the new level and the new exp
        """
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

    

    @lvl_group.command(name="leaderboard", description="Shows the 10 users with the highest levels")
    async def slash_leaderboard(self, interaction: discord.Interaction):
        """
        Display the 10 members of the server with the higher levels.
        USAGE: /leaderboard

        """
        dataDict = level.loadData()
        sorted_users = sorted(dataDict.items(), key=lambda x: (x[1]['level'], x[1]['exp']), reverse=True)
        embed = discord.Embed(title="LEADERBOARD", color=discord.Color.blue())
        for i, (userID, _) in enumerate(sorted_users[:10], start=1):
            member = await self.bot.fetch_user(int(userID))
            embed.add_field(name=member.name, value=f"level : {dataDict[str(userID)]['level']}\nexp : {dataDict[str(userID)]['exp']}")
        await interaction.response.send_message(embed=embed)







    
async def setup(bot):
    await bot.add_cog(LvlCmd(bot))
