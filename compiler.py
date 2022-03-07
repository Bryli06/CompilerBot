import discord
from discord.utils import get
from os import listdir
from os.path import isfile, join
from discord.ext import commands
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(),help_command=None)
TOKEN = ('')



if __name__ == '__main__':
    for cogs in [file.replace('.py', '') for file in listdir("Cogs") if isfile(join('Cogs',file))]:
        try:
            bot.load_extension('Cogs'+'.'+cogs)
        except Exception as e:
            print(e)

@bot.event
async def on_ready():
    print("Logged in")

bot.run(TOKEN)