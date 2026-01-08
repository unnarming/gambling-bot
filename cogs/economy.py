from discord.ext import commands
from cogs.misc import MiscCog
from embeds import Embeds
from config import Config
from sql import Sql
import discord
from utils import Int
import random
from utils import Check, Status
from cogs.events import EventsCog
from typing import List
from sql.user import User
from cogs.misc import MiscCog

class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Config, sql: Sql):
        self.bot = bot
        self.config: Config = config
        self.sql: Sql = sql
        self.embeds: Embeds = Embeds(config)

    @commands.command(name="balance", aliases=["bal"], description="Check your or another user's balance")
    async def balance(self, ctx: commands.Context, user: discord.Member = None):
        bal: int = self.sql.get_balance(user.id) if user else self.sql.get_balance(ctx.author.id)
        await ctx.send(embed=self.embeds.success(f"Balance: {bal}"))

    @commands.command("modify", description="Modify another user's balance")
    @commands.check(lambda ctx: MiscCog.check_permission(ctx.bot.get_cog("EconomyCog"), ctx))
    async def modify(self, ctx: commands.Context, user: discord.Member, amount: Int.Any()):
        self.sql.modify_balance(user.id, amount)
        await ctx.send(embed=self.embeds.success(f"Balance modified for {user.mention}: {amount}"))
    
    @commands.command("setbalance", aliases=["sb"], description="Set another user's balance")
    @commands.check(lambda ctx: MiscCog.check_permission(ctx.bot.get_cog("EconomyCog"), ctx))
    async def setbalance(self, ctx: commands.Context, user: discord.Member, amount: Int.Pos()):
        self.sql.set_balance(user.id, amount)
        await ctx.send(embed=self.embeds.success(f"Balance set for {user.mention}: {amount}"))

    @commands.command("beg", description="Beg for money")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(MiscCog.bot_channel_check)
    async def beg(self, ctx: commands.Context):
        if self.sql.get_balance(ctx.author.id) > 100000:
            return await ctx.send(embed=self.embeds.error("You're too rich to beg"))
        if random.random() < 0.8333333333333334:
            beg_opts: list[int] = [50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 300, 300, 300, 300, 300, 300, 500, 900, 500, 900, 2000]
            robbed_opts: list[int] = [50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 300, 300, 300, 300, 300, 300, 500, 900, 500, 900, 1000]
            amount: int = random.choice(beg_opts) if random.random() < 0.8333333333333334 else -random.choice(robbed_opts)
            self.sql.modify_balance(ctx.author.id, amount)
            if amount > 0:
                await ctx.send(embed=self.embeds.base(title="Beg result", description=f"If you're a broke boy just say so... you got {amount} money", color="success"))
            else:
                await ctx.send(embed=self.embeds.base(title="Beg result", description=f"Get fucking robbed pooron, you lost {amount} money", color="error"))
        else:
            await ctx.send(embed=self.embeds.base(title="Beg result", description=f"Fuck off poor boy", color="error"))

    @commands.command("baltop", description="View the top 10 balances")
    async def baltop(self, ctx: commands.Context):
        users: List["User.UserData"] = self.sql.get_highest_balances(10)
        await ctx.send(embed=self.embeds.base(title="Top 10 balances", description=f"{'\n'.join([f'<@{user.discord_id}> - ``{user.balance}``' for user in users])}", color="success"))
