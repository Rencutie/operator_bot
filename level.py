import json
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta


async def onLevel(message, userID, username):
    """
        get userID
        call loadData
        call checkUserLastText
        if true, call addExp
        check if they level up and call level up text

        does not return 
    """
    userData = loadData(userID)

    if checkUserLastText(userData):
        updateUserLastText(userData)
        addExp(userID)

def loadData(userID, username):
    """
        open json and return disctionary of the user data
        if user not inside, return a call of createUser
    """

    with open('level.json', 'r') as file :
        dataList = json.load(file)

    userData = next((user for user in dataList if user['userID'] == userID), None)
    if userData : 
        return userData
    return createUser(dataList, userID, username)


def createUser(data, userID, username):
    """
        make a new json object 
        should be sorted by userID 
        userID, level 0, exp 0, username, and lastText 0
        return dictionary of its data
    """
    userDict = {'userID' : userID, 'level' : 0, 'exp' : 0, "username" : username, 'lastText' : 0}
    data.append(userDict)
    with open('level.json', 'w') as file:
        json.dump(data, file, indent=4)
    return userDict

def checkUserLastText(userData):
    """
        check the last time the
        user got exp added and
        return true if it's more than 60s ago 
        or if last time is 0 (first text)
    """
    lastText = userData['lastText']
    if lastText ==0:
        return True
    current_time = datetime.now()
    last_message_time = datetime.fromisoformat(lastText)
    time_difference = current_time - last_message_time
    if time_difference < timedelta(minutes=1):
        return True
    return False
    TODO

def updateUserLastText(userData, userID):
    """
        userData : a dict of the datas of the user we want to update
        write the current time to 'lastText'
        in a ISO format to the Json
        does not return
    """
    current_time = datetime.now()
    userData['lastText'] = current_time
    
    with open('level.json', 'r') as file:
        all_user_data = json.load(file)
    all_user_data[userID] = userData

    with open('level.json', 'w') as file:
        json.dump(all_user_data, file, indent=4)
    

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
