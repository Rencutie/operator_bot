import discord
from discord.ext import commands
import level

class LvlCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def lvl(ctx, member: discord.Member = None):
        if member == None :
            userID = str(ctx.author.id)
        else :
            userID = member.id
        dataDict = level.loadData()
        await ctx.send(f"{ctx.author.name}, your current level is {dataDict[userID]['level']}\nYour current exp is {dataDict[userID]['exp']} out of {level.xp_requirements[dataDict[userID]['level']]} required to level up.")

    @commands.command()
    @commands.has_permissions(administration=True)
    async def addExp(ctx, member: discord.Member, amount):
        userID = str(member.id)
        dataDict = level.loadData()
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
    async def setLvl(ctx, member: discord.Member, lvl):
        userID= str(member.id)
        dataDict = level.loadData()
        initLvl = dataDict[userID]['level']
        dataDict[userID]['level'] = lvl
        dataDict[userID]['exp'] = 0
        level.saveData(dataDict)
        await ctw.send(f"Set {member.mention} level to {lvl}\nWas {initLvl}")
    
    @commands.command()
    @commands.has_permissions(administration=True)
    async def rmexp(ctx, member: discord.Member, amount):
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

    
