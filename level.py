import json
import discord
from discord import app_commands
from discord.ext import commands


async def onLevel(message, userID):
    """
        get userID
        call loadData
        call checkUserLastText
        if true, call addExp
        check if they level up and call level up text

        does not return 
    """
    if message.author.bot:
        return
    userData = loadData(userID)
    if checkUserLastText(userData):
        addExp(userID)

def loadData(userID):
    """
        open json and return disctionary
        if user not inside, return a call of createUser
    """
    with open('level.json', 'r') as file :
        dataList = json.load(file)
    userData = next((user for user in dataList if user['userID'] == userID), None)
    if userData is not None: 
        return userData
    return createUser(userID)

def createUser(userID):
    """
        make a new json object 
        should be sorted by userID 
        level 0, 0 exp, username
        return dictionary of its data
    """
    TODO

def checkUserLastText(userData):
    """
        check the last time the
        user got exp added and
        return true if it's more than 60s ago
    """
    TODO

def checkLvlUp(userData):
    """
        get the user's level, and check if his exp is more
        than the treshold for a lvl up. return True(lvl up) or False(not lvl up)
    """
    TODO

def addExp(userData):
    """
        add a random number between 7 and 13 to the
        users exp 
    """
    TODO

async def levelUpMessage(userData):
    """
        send a pretty message with the level archived and username
        userData : dictionary
    """
    TODO


@bot.command
async def level(ctx):
    # userID = [TODO]
    # userData = loadData
    # message with current lvl and exp
    pass
