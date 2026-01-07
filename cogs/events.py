import discord
from discord.ext import commands
from embeds import Embeds
from config import Config
from sql import Sql
import os

class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Config, sql: Sql):
        self.bot = bot
        self.config: Config = config
        self.embeds: Embeds = Embeds(config)
        self.sql: Sql = sql

    class WrongChannel(commands.CommandError):
        def __init__(self, message: str):
            super().__init__(message)
            self.message = message

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}')
        synced = await self.bot.tree.sync()
        print(f'Synced {len(synced)} commands')

    # error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(embed=self.embeds.error("Command not found"))
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=self.embeds.error("Missing required argument"))
            return
        elif isinstance(error, commands.BadArgument):
            await ctx.send(embed=self.embeds.error("Invalid arguments"))
            return
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(embed=self.embeds.error("Invalid argument format"))
            return
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(embed=self.embeds.error("Check failure"))
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=self.embeds.error(f"Command on cooldown, try again in {error.retry_after:.2f} seconds"))
            return
        elif isinstance(error, self.WrongChannel):
            await ctx.send(embed=self.embeds.error(error.message))
            return
        else:
            await ctx.send(embed=self.embeds.error(str(error)))
            return