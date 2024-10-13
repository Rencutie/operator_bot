import json
from datetime import datetime, timedelta
import random
async def onLevel(message, userID, username):
    """
        get userID
        call loadData
        call checkUserLastText
        if true, call addExp
        check if they level up and call level up text

        does not return 
    """
    dataDict = loadData()
    if userID not in dataDict :
        createUser(dataDict, userID, username)
    # no save because checkUserLastText is true 
    # if just created
    if checkUserLastText(dataDict, userID):
        updateUserLastText(dataDict, userID)
        addExp(dataDict, userID)
        if checkLvlUp(dataDict, userID):
            levelUpMessage(dataDict, userID)
        saveData(dataDict)

def loadData():
    """
        read the json file and return the data
    """
    with open('level.json', 'r') as file :
        return json.load(file)

def saveData(dataDict):
    with open('level.json', 'w') as file:
        json.dump(dataDict, file, indent=4)

def createUser(dataDict, userID, username):
    """
    Make a new user entry and add it to the dataDict.
    """
    userDict = {'userID': userID, 'level': 1, 'exp': 0, "username": username, 'lastText': 0}
    dataDict[userID] = userDict


def checkUserLastText(dataDict, userID):
    """
        check the last time the
        user got exp added and
        return true if it's more than 60s ago 
        or if last time is 0 (first text)
    """
    lastText = dataDict[userID]['lastText']
    if lastText == 0:
        return True
    current_time = datetime.now()
    last_message_time = datetime.fromisoformat(lastText)
    time_difference = current_time - last_message_time
    if time_difference > timedelta(minutes=1):
        return True
    return False

def updateUserLastText(dataDict, userID):
    """
        write the current time to 'lastText'
        in a ISO format
    """
    current_time = datetime.now()
    dataDict[userID]['lastText'] = current_time.isoformat()


def checkLvlUp(dataDict, userID):
    """
        get the user's level, and check if his exp is more
        than the treshold for a lvl up. return True(lvl up) or False(not lvl up)
    """
    current_level = dataDict[userID]['level']
    required_xp = xp_requirements[current_level]
    if dataDict[userID]['exp'] >= required_xp:
        dataDict[userID]['level'] += 1
        dataDict[userID]['exp'] = dataDict[userID]['exp'] - required_xp
        return True
    return False
    TODO

def addExp(dataDict, userID):
    """
        add a random number between 7 and 13 to the
        users exp 
    """
    dataDict[userID]['exp'] = dataDict[userID]['exp'] + random.randint(7, 13)

async def levelUpMessage(message, dataDict, userID):
    """
        send a pretty message with the level archived and username
        userData : dictionary
    """
    await ctx.send(f"Congratulations, {message.author.mentiop}! You have reached level {dataDict[userID]['level']}")




def generate_level_xp(max_level=100, base_xp=100, growth_rate=1.1):
    """
    Generate a dictionary with required XP for leveling up.
    
    :param max_level: The maximum level to generate XP for.
    :param base_xp: The XP required for the first level up.
    :param growth_rate: The rate at which XP requirement grows.
    :return: A dictionary with level as keys and required XP as values.
    """
    level_xp = {}
    current_xp = base_xp
    
    for level in range(1, max_level + 1):
        level_xp[level] = round(current_xp)
        current_xp *= growth_rate  # Increase required XP by growth rate
    
    return level_xp

# Execute the function when the module is imported
xp_requirements = generate_level_xp()

# Optionally print the XP requirements
for level, xp in xp_requirements.items():
    print(f"Level {level}: {xp} XP")