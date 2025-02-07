from discord.ext import commands
import asyncio
from discord import app_commands
from discord import FFmpegPCMAudio
from pytube import Playlist

import discord
import json
import yt_dlp

from error_handling import send_log

class Music(commands.Cog):
    """
    everything related to the bot playing music in voice channels
    is defined here
    """
    def __init__(self, bot):
        self.bot = bot
        self.music_queue = [] # (title, stream url)
        with open("storage/config.json", "r") as file:
            self.config = json.load(file)
        self.log_channel_id = self.config.get("channel", {}).get("log_channel_id", -1)
        self.voice_client = None
        self.current_track = None

    
    music_group = app_commands.Group(name="music", description="Commands used to play music in vc")

    
    async def fetch_metadata(self, video_url):
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}

        try:
            # Use yt_dlp to fetch video metadata synchronously
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

            # Find an audio stream URL
            audio_url = next(
                (f['url'] for f in info['formats'] if f.get('acodec') != 'none' and 'url' in f),
                None
            )
            title = info.get('title', 'Unknown Title')

            if not audio_url:
                return 'Unknown Title', None

            return title, audio_url

        except Exception as e:
            print(f"Error fetching metadata: {e}")
            return 'Unknown Title', None

    @music_group.command(name="join", description="Join a voice channel the user is in")
    async def slash_join(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            voice_channel = interaction.user.voice.channel
            if interaction.guild and interaction.guild.voice_client:
                await interaction.guild.voice_client.move_to(voice_channel)
            else:
                self.voice_client = await voice_channel.connect()
            await interaction.response.send_message(f"Joined {voice_channel.name}.")
            await send_log(self.bot, f"{interaction.user.name} made the bot join {voice_channel.name}", self.log_channel_id)
        else:
            await interaction.response.send_message("You need to be in a voice channel to use this command.", ephemeral=True)




    @music_group.command(name="add_queue", description="add a song from a youtube url to the music queue")
    async def add_queue(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        if self.voice_client is None:
            await interaction.edit_original_response(content="The bot is not connected to any voice channel.")
            return

        if interaction.user.voice and interaction.user.voice.channel == self.voice_client.channel:
            # Get the audio source for the URL and append it to the music queue
            try:
                title, url = await self.fetch_metadata(url)
            except Exception :
                await interaction.edit_original_response(content=f"Failed to get audio source for {url}.\nPlease ensure you entered a Youtube")
                return
            self.music_queue.append((title, url))
            await interaction.edit_original_response(content=f"Added {title} to the music queue.")
            
            # Check if the bot is not currently playing music
            if not self.voice_client.is_playing():
                await self.play_music()  # Await the play_music coroutine
        else:
            await interaction.edit_original_response(content="You need to be in the same voice channel as the bot to use this command.")
    


    @music_group.command(name="add_playlist", description="add an entire playlist to the music queue")
    async def add_playlist(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        if self.voice_client is None:
            await interaction.edit_original_response(content="the bot is not in a voice channel")
            return

        if interaction.user.voice and interaction.user.voice.channel == self.voice_client.channel:
            try:
                list_url = get_urls_playlist(url)
                
                for song_url in list_url:
                    try: 
                        title, url = await self.fetch_metadata(song_url)

                    except Exception as e:
                        print(f"Failed to get audio source for {song_url}. Skipping...")
                        continue
                    self.music_queue.append((title, url))
                    # start music if not ongoing already
                    # placed here cause it might be really long to laod
                    # a big playlist
                    if not self.voice_client.is_playing():
                        await self.play_music() 
                await interaction.edit_original_response(content=f"Added {len(list_url)} songs to the music queue.")

            except Exception as e:  
                print(e)
                await interaction.edit_original_response(
                    content=f"Failed to get audio sources for {url}. Please ensure it's a valid YouTube playlist URL.")
                return




    @music_group.command(name="skip", description="skips the current song")
    async def slash_skip(self, interaction: discord.Interaction):
        if self.voice_client is None:
            await interaction.response.send_message("The bot is not connected to any voice channel.", ephemeral=True)
            return

        if interaction.user.voice and interaction.user.voice.channel == self.voice_client.channel :
            if self.music_queue:
                self.voice_client.stop() # stops to triger "after"
                await interaction.response.send_message("Skipped the current song.")
            else: 
                await interaction.response.send_message("The queue is empty.")
        else:
            await interaction.response.send_message("You need to be in the same voice channel as the bot to use this command.", ephemeral=True)



    @music_group.command(name="pause", description="pause the music")
    async def pause(self, interaction: discord.Interaction):
        if self.voice_client is None:
            await interaction.response.send_message("The bot is not connected to any voice channel.", ephemeral=True)
            return

        if interaction.user.voice and interaction.user.voice.channel == self.voice_client.channel:
            if self.voice_client.is_playing():
                self.voice_client.pause()
                await interaction.response.send_message("Paused the music.")
            else:
                await interaction.response.send_message("The music is not currently playing.")
        else:
            await interaction.response.send_message("You need to be in the same voice channel as the bot to use this command.", ephemeral=True)


    @music_group.command(name="resume", description="resume the music")
    async def resume(self, interaction: discord.Interaction):
        if self.voice_client is None:
            await interaction.response.send_message("The bot is not connected to any voice channel.", ephemeral=True)
            return

        if interaction.user.voice and interaction.user.voice.channel == self.voice_client.channel:
            if self.voice_client.is_paused():
                self.voice_client.resume()
                await interaction.response.send_message("Resumed the music.")
            else:
                await interaction.response.send_message("The music is not currently paused.")
        else:
            await interaction.response.send_message("You need to be in the same voice channel as the bot to use this command.", ephemeral=True)


    @music_group.command(name="stop", description="stops the current song and clears the queue")
    async def slash_stop(self, interaction: discord.Interaction):
        if self.voice_client is None:
            await interaction.response.send_message("The bot is not connected to any voice channel.", ephemeral=True)
            return

        if interaction.user.voice and interaction.user.voice.channel == self.voice_client.channel :
            if self.voice_client:
                self.voice_client.stop()
                self.music_queue.clear()
                self.current_track =  None
                await self.voice_client.disconnect()
                await interaction.response.send_message("Stopped the music and cleared the queue.")
            else : 
                await interaction.response.send_message("The bot is not currently connected to a voice channel.")
        else:
            await interaction.response.send_message("You need to be in the same voice channel as the bot to use this command.", ephemeral=True)
    
    



    @music_group.command(name="show_queue", description="display the waiting queue")
    async def show_queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.voice_client is None:
            await interaction.followup.send("The bot is not connected to any voice channel.", ephemeral=True)
            return
        embed = discord.Embed(title="Current Queue", color=discord.Color.blue())
        try:
            embed.add_field(name="currently playing", value=self.current_track)
            for i, music in enumerate(self.music_queue, start=0):
                embed.add_field(name=f"Song {i+1}", value=music[0], inline=False)
            await interaction.followup.send(embed=embed)
        except Exception :
            await interaction.followup.send(f"Failed to get current queue information. The queue is probably empty")
    

    async def play_music(self):
        if self.music_queue and self.voice_client and not self.voice_client.is_playing():
            title, audio_source = self.music_queue.pop(0)

            # Check if audio_url is valid
            if audio_source is None:
                send_log(self.bot, f"error getting audio url for {title}", self.log_channel_id)
                await self.play_music()  # Try the next song in the queue
                return

            try:
                 
                # Create the audio source with FFmpeg options to handle reconnecting if needed
                audio_source = FFmpegPCMAudio(
                    audio_source,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                )

                # Play the audio and set up a callback for when it finishes
                self.voice_client.play(
                    audio_source,
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_music(), self.bot.loop)
                )
                self.current_track = title  # Set current track

            except Exception as e:
                print(f"Failed to play {title}: {e}")
                await send_log(self.bot, f"Failed to play music: {title}. Error: {e}", self.log_channel_id)
                self.current_track = None  # Clear current track
                await self.play_music()  # Move to the next song in the queue if available



def get_urls_playlist(playlist_url):
    urls = []
    vids_Urls = Playlist(playlist_url)
    for url in vids_Urls:
        urls.append(url)
    return urls

async def setup(bot):
    await bot.add_cog(Music(bot))
