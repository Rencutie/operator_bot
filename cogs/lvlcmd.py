import discord
from discord.ext import commands
import level

class LvlCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def lvl(self, ctx, member: discord.Member = None):
        if member == None :
            userID = str(ctx.author.id)
        else :
            userID = str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await ctx.send(f"{member.mention} is not in the database.\nPrehaps they never sent a message")
            return
        current_lvl = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp']
        await ctx.send(f"{ctx.author.name}, your current level is {dataDict[userID]['level']}\nYour current exp is {dataDict[userID]['exp']} out of {level.xp_requirements[dataDict[userID]['level']]} required to level up.")

    @commands.slash_command(name ="lvl", description="show a user's level. Show self if no user is given")
    async def slash_lvl(self, ctx, member: discord.Member = None):
        if member == None :
            userID = str(ctx.author.id)
        else :
            userID = str(member.id)
        dataDict = level.loadData()
        
        if userID not in dataDict:
            await ctx.send(f"{member.mention} is not in the database.\nPrehaps they have never sent a message")
            return

        await ctx.send(f"{ctx.author.name}, your current level is {dataDict[userID]['level']}\nYour current exp is {dataDict[userID]['exp']} out of {level.xp_requirements[dataDict[userID]['level']]} required to level up.")


    @commands.command()
    @commands.has_permissions(administration=True)
    async def addExp(self, ctx, member: discord.Member, amount:int):
        userID = str(member.id)
        dataDict = level.loadData()
        #check if in database, create user if not
        if userID not in dataDict:
            await ctx.send (f"{member.mention} does not exist in the database, creating {member.mention}")
            level.createUser(dataDict, userID, member.name)

        current_level = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp'] + amount
        treshold = level.xp_requirements[current_level]
        while current_exp >= treshold :
            current_level += 1
            current_exp -= treshold
            treshold = level.xp_requirements[current_level]
        dataDict[userID]['level'] = current_level
        dataDict[userID]['exp'] = current_exp
        level.saveData(dataDict)
        await ctx.send(f"added {amount} exp to {member.mention} \nNew Level : {current_level}\nNew exp : {current_exp}")
    
    @commands.slash_command(name="addExp", description="add a said amount of exp to a user")
    @commands.has_permissions(administration=True)
    async def slash_addExp(self, ctx, member: discord.Member, amount:int):
        userID = str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await ctx.send (f"{member.mention} does not exist in the database, creating {member.mention}")
            level.createUser(dataDict, userID, member.name)
        current_level = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp'] + amount
        treshold = level.xp_requirements[current_level]
        while current_exp >= treshold :
            current_level += 1
            current_exp -= treshold
            treshold = level.xp_requirements[current_level]
        dataDict[userID]['level'] = current_level
        dataDict[userID]['exp'] = current_exp
        level.saveData(dataDict)
        await ctx.send(f"added {amount} exp to {member.mention}")


    @commands.command()
    @commands.has_permissions(administration=True)
    async def setLvl(self, ctx, member: discord.Member, lvl:int):
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


    @commands.slash_command(name="addExp", description="set a user's level to a given number")
    @commands.has_permissions(administration=True)
    async def slash_setLvl(self, ctx, member: discord.Member, lvl:int):
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
    

    @commands.command()
    @commands.has_permissions(administration=True)
    async def rmExp(self, ctx, member: discord.Member, amount:int):
        userID = str(member.id)
        dataDict = level.loadData()
        if userID not in dataDict:
            await ctx.respond(f"{member.mention} does not exist in database, you cannot remove them exp as they have none.")
        current_lvl = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp']
        while amount > 0:
            if current_exp < amount:
                amount -= current_exp
                current_exp = 0
                if current_lvl > 1 :
                    current_lvl -= 1
                    current_exp = level.xp_requirements[current_lvl]
            else:
                current_exp -= amount
                amount = 0
        dataDict[userID]['level'] = current_lvl
        dataDict[userID]['exp'] = current_exp
        level.saveData(dataDict)
        await ctx.send(f"Removed experience points from {member.mention}. They are now at level {current_lvl} with {current_exp} exp.")

    
    @commands.slash_command(name="rmExp", description="remove a said amount of exp to a user")
    @commands.has_permissions(administration=True)
    async def slash_rmExp(self, ctx, member:discord.Member, amount:int):
        userID = str(member.id)
        dataDict = level.loadData()
        current_lvl = dataDict[userID]['level']
        current_exp = dataDict[userID]['exp']
        while amount > 0:
            if current_exp < amount:
                amount -= current_exp
                current_exp = 0
                if current_lvl > 1 :
                    current_lvl -= 1
                    current_exp = level.xp_requirements[current_lvl]
            else:
                current_exp -= amount
                amount = 0
        dataDict[userID]['level'] = current_lvl
        dataDict[userID]['exp'] = current_exp
        level.saveData(dataDict)
        await ctx.send(f"Removed experience points from {member.mention}. They are now at level {current_lvl} with {current_exp} exp.")