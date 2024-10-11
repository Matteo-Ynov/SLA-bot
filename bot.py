import os
from nextcord import Intents
from nextcord.ext import commands
from config import BOT_TOKEN, PROJECT_PATH

intents = Intents.default()
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

if __name__ == "__main__":
    for filename in os.listdir(f"{PROJECT_PATH}/commands"):
        if filename.endswith(".py"):
            bot.load_extension(f"commands.{filename[:-3]}")

    bot.run(BOT_TOKEN)
