from discord.ext import commands
from embeds import Embeds
from config import Config
from sql import Sql
from cogs.events import EventsCog
from utils import Check

class MiscCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Config, sql: Sql):
        self.bot = bot
        self.config: Config = config
        self.sql: Sql = sql
        self.embeds: Embeds = Embeds(config)

    def check_permission(self, ctx: commands.Context) -> bool:
        return ctx.author.id in self.config.permission_whitelist_uids

    def bot_channel_check(ctx: commands.Context) -> bool:
        misc_cog = ctx.bot.get_cog("MiscCog")
        if ctx.channel.id != misc_cog.config.bot_channel:
            raise EventsCog.WrongChannel(message=Check.BOT_CHANNEL.to_status().message)

        if isinstance(ctx.channel, discord.DMChannel) and not misc_cog.config.ENABLE_DMS:
            raise EventsCog.WrongChannel(message=Check.BOT_CHANNEL.to_status().message)
        
        return True

    @commands.command(name="test", description="Test the bot")
    async def ping(self, ctx: commands.Context):
        await ctx.send(embed=self.embeds.error("Test"))
