import discord
from discord.ext import commands
from sql import Sql
from embeds import Embeds
from config import Config
from sql.structs import CoinflipStats
from utils import Status, Int
from sql.coinflip import Coinflip
from typing import List, Literal
from cogs.misc import MiscCog

class CoinflipCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Config, sql: Sql):
        self.bot = bot
        self.config: Config = config
        self.sql: Sql = sql
        self.embeds: Embeds = Embeds(config)

    # coinflip group
    # $cf <user> <amount> to challenge a user to a coinflip
    # $cf self <amount> to coinflip yourself
    # $cf stats <user=None> to view your or another user's coinflip statistics
    # $cf public <amount> to make a public coinflip
    # $cf accept <id/user> to accept a public coinflip/request
    # $cf view <self/public/requests> to view your coinflip requests/public coinflips
    @commands.group(name="coinflip", aliases=["cf"], invoke_without_command=True, description="Coinflip with a user")
    async def coinflip(self, ctx: commands.Context, user: discord.Member | None = None, amount: Int.Pos = 100):
        if user is None:
            return await ctx.send(embed=self.embeds.error("Please specify a user to challenge"))
        res: Status = self.sql.make_coinflip(ctx.author.id, user.id, amount)
        if not res.status:
            return await ctx.send(embed=self.embeds.error(res.message))
        
        return await ctx.send(embed=self.embeds.success(f"Coinflip challenge sent to {user.mention}"))

    @coinflip.command(name="self", description="Coinflip yourself")
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.check(MiscCog.bot_channel_check)
    async def self(self, ctx: commands.Context, amount: Int.Pos()):
        cf_res: Status = self.sql.self_coinflip(ctx.author.id, amount)
        if not cf_res.status:
            return await ctx.send(embed=self.embeds.error(cf_res.message))
        
        cf_res.body["winner"]
        if cf_res.body["winner"] == ctx.author.id:
            return await ctx.send(embed=self.embeds.success(f"You won the coinflip and gained {cf_res.body['amount']} money"))
        else:
            return await ctx.send(embed=self.embeds.error(f"You lost the coinflip and lost {cf_res.body['amount']} money"))

    @coinflip.command(name="stats", description="View your or another user's coinflip statistics")
    async def stats(self, ctx: commands.Context, user: discord.Member | None = None):
        if user is None:
            return await ctx.send(embed=self.embeds.error("Please specify a user to view statistics"))
        cf_stats: CoinflipStats = self.sql.get_stats(user.id, "cf_stats")
        mlostto: discord.User = self.bot.fetch_user(cf_stats.most_lost_to_id)
        return await ctx.send(embed=self.embeds.success(f"Statistics for {user.mention}:\nGames won: {cf_stats.games_won}\nGames lost: {cf_stats.games_lost}\nMoney won: {cf_stats.money_won}\nMoney lost: {cf_stats.money_lost}\nMost lost: {cf_stats.most_lost}\nMost lost to: {mlostto.mention}\nLoss streak: {cf_stats.loss_streak}"))

    @coinflip.command(name="accept", description="Accept a coinflip request")
    async def accept(self, ctx: commands.Context, user: discord.Member | None = None, id: str | None = None):
        if user is None and id is None:
            return await ctx.send(embed=self.embeds.error("Please specify a user or id to accept"))
        res: Status = self.sql.accept_coinflip(ctx.author.id, user.id if user else None, id)
        if not res.status:
            return await ctx.send(embed=self.embeds.error(res.message))
        
        cf: Coinflip.CoinflipData = res.body
        # send a embed with the coinflip details (winner, loser, amount)
        return await ctx.send(embed=self.embeds.success(f"<@{cf["winner"]}> just beat <@{cf["loser"]}> in a coinflip of {cf["amount"]}"))

    @coinflip.command(name="view", description="View your coinflip requests/public coinflips")
    async def view(self, ctx: commands.Context, type: str = Literal["requests", "public", "self"]):
        if type == "requests":
            res: Status = self.sql.get_coinflips_by_user_opponent(ctx.author.id)
            if not res.status:
                return await ctx.send(embed=self.embeds.error(res.message))
            cf: List[Coinflip.CoinflipData] = res.body
            return await ctx.send(embed=self.embeds.success(f"Coinflip requests:\n{'\n'.join([f'<@{cf.requester_id}> vs <@{cf.opponent_id}> for {cf.amount}' for cf in cf])} | ``{cf.id}``"))
        elif type == "public":
            res: Status = self.sql.get_public_cf()
            if not res.status:
                return await ctx.send(embed=self.embeds.error(res.message))
            cf: List[Coinflip.CoinflipData] = res.body
            return await ctx.send(embed=self.embeds.success(f"Public coinflips:\n{'\n'.join([f'<@{cf.requester_id}> vs <@{cf.opponent_id}> for {cf.amount}' for cf in cf])} | ``{cf.id}``"))
        elif type == "self":
            res: Status = self.sql.get_coinflips_by_user(ctx.author.id)
            if not res.status:
                return await ctx.send(embed=self.embeds.error(res.message))
            cf: List[Coinflip.CoinflipData] = res.body
    
            return await ctx.send(embed=self.embeds.success(f"Coinflip requests:\n{'\n'.join([f'<@{cf.requester_id}> vs <@{cf.opponent_id}> for {cf.amount}' for cf in cf])} | ``{cf.id}``"))
        else:
            return await ctx.send(embed=self.embeds.error("Invalid type"))
