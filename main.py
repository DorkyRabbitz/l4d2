import asyncio
import inspect
import platform
import time
from os import getcwd, getenv, makedirs, path

import discord
from colorama import Back, Fore, Style
from discord.ext import commands

from dotenv import load_dotenv ; load_dotenv()

import settings
import platform
import cpuinfo

class Bot(commands.Bot):
    """Initializes the bot and it's modules, as well as the error handler"""
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('>.<'), intents=discord.Intents().all())

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error:discord.app_commands.CommandInvokeError):
            # Get the frame where the exception occurred
            frame = inspect.currentframe().f_back

            # Get information about the occurence
            line_number = frame.f_lineno
            file_path = inspect.getframeinfo(frame).filename
            filename = path.basename(inspect.getframeinfo(frame).filename)
            log = f"{time.strftime('%d/%m/%Y %H:%M:%S UTC')}\nException: {interaction.command.module}.{interaction.command.name}:\nFile: {filename} {'(External)' if file_path != getcwd() else ''}, line {line_number}\n{error.original}"

            if isinstance(error.original, AttributeError):
                if not path.isdir("./logs"):
                    makedirs("./logs")
                await interaction.channel.send(f"An uncaught error has occurred, this occurrence has been automatically reported to your maintainer!\nHere's the log:\n```{log}```")
                logger = open(f"./logs/UncaughtException_{time.strftime('%d-%m-%Y %H-%M-%S UTC')}.txt","w",encoding="utf-8")
                print(log,file=logger)
                logger.close()
            
            elif isinstance(error.original, discord.errors.InteractionResponded):
                print(f"Interaction already acknowledged, {interaction.command.module}.{interaction.command.name}")

            elif isinstance(error.original, discord.app_commands.MissingPermissions):
                await interaction.channel.send("You don't have permission to run that command!",ephemeral=True)
            
            elif isinstance(error.original, discord.app_commands.BotMissingPermissions):
                await interaction.channel.send("I don't have permission to do that!",ephemeral=True)
            
            elif isinstance(error.original, discord.app_commands.MissingPermissions):
                await interaction.channel.send("You don't have permission to run that command!",ephemeral=True)
            else:
                await interaction.channel.send(f"An uncaught exception has occurred, this occurrence has been automatically reported to your maintainer!:\nHere's the log:\n```{log}```")
                logger = open(f"./logs/UncaughtException_{time.strftime('%d-%m-%Y %H:%M:%S UTC')}.txt","w",encoding="utf-8")
                print(log,file=logger)
                logger.close()


    async def setup_hook(self):
        for key, value in settings.modules.items():
            if value:
                if path.isfile(f"modules/{key}.py"):
                    await self.load_extension(f"modules.{key}")
                elif path.isdir(f"modules/{key}"):
                    await self.load_extension(f"modules.{key}.{key}")
                else:
                    print(f"The module {key} files are missing!")
        await self.tree.sync()       

    async def on_ready(self):
        #Status task, updates the bot's presence every minute
        async def status_task(self):
            while True:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name="past you nerds!",url="https://www.youtube.com/watch?v=HZCKddHYgPM"))
                await asyncio.sleep(60)
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="with you nerds!"))
                await asyncio.sleep(60)

        bot.loop.create_task(status_task(self))
        prfx = (Back.BLACK + Fore.MAGENTA + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + f" Logged in as {Fore.MAGENTA}{self.user.name}{Fore.RESET}")
        print(prfx + f" Running on {Fore.GREEN}{settings.mode.lower()}{Fore.RESET} mode")
        print(prfx + f" OS: {Fore.CYAN}{platform.platform()} / {platform.release()}{Fore.RESET}")
        print(prfx + f" CPU: {Fore.CYAN}{cpuinfo.get_cpu_info()['brand_raw']}{Fore.RESET}")
        print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()) + Fore.WHITE)
        print(prfx + " Discord.py Version " + Fore.YELLOW + discord.__version__ + Fore.RESET)
        


bot = Bot()
if settings.mode.lower() == "retail":
    bot.run(getenv("token")) 
elif settings.mode.lower() == "development":
    bot.run(getenv("development_token"))
else:
    print("You forgot to set the runtime mode, dumbass")