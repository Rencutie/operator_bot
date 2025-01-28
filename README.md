A discord bot made in Python that support being only on a single server. 
You can use this as an exemple of how to make your own and/or use it as a template. 

# FEATURES :
- Basic moderation tools <br> 
- Join and leave messages <br>
- Role interactions <br>
- Join and play music from youtube in voice chat with a support for playlist <br>
- Textual level system <br>
- random nsfw media matching given tags using rule34 API <br>

# WIP :
- Using command tree for more understandable navigation (/ban -> /moderation ban for exemple)

# TODO :
- Switching the json storage with an SQLite database

# DEPENDENCIES : 
You can install all required dependencies by typing  
``pip install -r requirement.txt``
<br>
Here is a breakthrough : 

> discord.py <br>

The python library for discord, quite usefull <br>

> pynacl, yt-dlp, audioo-lts, pytube <br>

These are used to extract and play audio content in voice chat from Youtube <br>

> python-dotenv

This is for importing sensitive data (here API keys) into the code

 
