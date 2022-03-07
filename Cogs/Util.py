import discord
from discord.ext import commands

class Util(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command(pass_context=True, name='help')
    async def purpose(self,ctx):
        embed=discord.Embed(title='Purpose of the bot', description='This bot is an compiler to a custom language\n'
                                                                    'To find out how to use this language, simply use the command doc',color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def doc(self,ctx):
        embed = discord.Embed(title='How to use the language', description='The documentation to the language\n'
                                                                           'I\'m dumb and havent finished this lmfao', color=0x00ff00)
        await ctx.send(embed=embed)
    @commands.command(pass_context=True)
    async def example(self,ctx):
        embed=discord.Embed(title="An example of code", description='```let a=0;\nlet b=1;\nlet i=0;\nwhile(i<20){\n\tprint(a);\n\tlet c=a+b;\n\tlet a=b;\n\tlet b=c;\n\tlet i=i+1;\n}```',color=discord.Colour.blurple())
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Util(bot))