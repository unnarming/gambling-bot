import secrets
from .sqlbase import SqlBase
from sqlalchemy import Column, BigInteger, String, DateTime, or_
from datetime import datetime, timedelta
import functools
import shortuuid
import secrets
import math
from .user import User
from utils import Status, Check
from .structs import CoinflipStats
from typing import List
from .user import usercheck

class Coinflip(SqlBase):
    class CoinflipData(SqlBase.Base):
        __tablename__ = "coinflips"

        id: str = Column(String, primary_key=True, index=True)
        requester_id: int = Column(BigInteger, nullable=False)
        opponent_id: int = Column(BigInteger, nullable=True)
        amount: int = Column(BigInteger, nullable=False)
        expires_at: datetime = Column(DateTime, nullable=False)

    def coinflip(self, requester_id: int = 0, req_loss_streak: int = 0, opponent_id: int | None = None, opp_loss_streak: int = 0, amount: int = 100) -> Status:
        odds: list[int] = [self.config.BASE_ODDS, self.config.BASE_ODDS]

        if req_loss_streak >= self.config.MAX_LOSS_STREAK:
            odds[0] = odds[0] * math.pow(req_loss_streak - self.config.MAX_LOSS_STREAK, self.config.STREAK_BIAS)
        if opp_loss_streak >= self.config.MAX_LOSS_STREAK:
            odds[1] = odds[1] * math.pow(opp_loss_streak - self.config.MAX_LOSS_STREAK, self.config.STREAK_BIAS)        

        total = sum(odds)
        odds = [odds[0] / total * 100, odds[1] / total * 100]
        rnd = secrets.randbelow(100)
        if rnd < odds[0]:
            winner = requester_id
            loser = opponent_id
        else:
            winner = opponent_id
            loser = requester_id
        
        return Status(status=True, body={
            "winner": winner,
            "loser": loser,
            "amount": amount
        })
        
    def create_coinflip(self, requester_id: int, opponent_id: int | None, amount: int) -> Status:
        with self.session() as session:
            coinflip = Coinflip.CoinflipData(
                id=shortuuid.ShortUUID().random(length=9),
                requester_id=requester_id,
                opponent_id=opponent_id,
                amount=amount,
                expires_at=datetime.now() + timedelta(minutes=2)
            )
            session.add(coinflip)
            session.commit()
            return Status(status=True, body=coinflip.id)

    def get_coinflip(self, id: str) -> Status:
        with self.session() as session:
            coinflip = session.query(Coinflip.CoinflipData).filter_by(id=id).first()
            if coinflip:
                return Status(status=True, body=coinflip)
            return Status(message="Coinflip doesn't exist")

    def get_coinflip_by_users(self, discord_id: int, opponent_id: int | None) -> Status:
        with self.session() as session:
            coinflip: Coinflip.CoinflipData = session.query(Coinflip.CoinflipData).filter(
                or_(
                    (Coinflip.CoinflipData.requester_id == discord_id) & (Coinflip.CoinflipData.opponent_id == opponent_id),
                    (Coinflip.CoinflipData.requester_id == opponent_id) & (Coinflip.CoinflipData.opponent_id == discord_id)
                )
            ).first()
            if coinflip:
                return Status(status=True, body=coinflip)
            return Status(message="Coinflip doesn't exist")

    @usercheck
    def get_coinflip_by_id(self, id: str) -> Status:
        with self.session() as session:
            coinflips: list["Coinflip.CoinflipData"] = session.query(Coinflip.CoinflipData).filter_by(id=id).all()
            if coinflips:
                return Status(status=True, body=coinflips)  
            return Status(message="Coinflips don't exist")

    @usercheck
    def get_coinflips_by_user(self, discord_id: int) -> Status:
        with self.session() as session:
            coinflips: List["Coinflip.CoinflipData"] = session.query(Coinflip.CoinflipData).filter_by(requester_id=discord_id).all()
            if coinflips:
                return Status(status=True, body=coinflips)
            return Status(message="Coinflips don't exist")
    
    @usercheck
    def get_coinflips_by_user_opponent(self, discord_id: int) -> Status:
        with self.session() as session:
            coinflips: List["Coinflip.CoinflipData"] = session.query(Coinflip.CoinflipData).filter_by(opponent_id=discord_id).all()
            if coinflips:
                return Status(status=True, body=coinflips)
            return Status(message="Coinflips don't exist")
        
    def delete_coinflip(self, id: str) -> Status:
        with self.session() as session:
            coinflip = session.query(Coinflip.CoinflipData).filter_by(id=id).first()
            if coinflip:
                session.delete(coinflip)
                session.commit()
                return Status(status=True, body=id)
            return Status(message="Coinflip doesn't exist")

    def clear_expired_coinflips(self):
        with self.session() as session:
            res = session.query(Coinflip.CoinflipData).all()
            for coinflip in res:
                if coinflip.expires_at < datetime.now():
                    session.delete(coinflip)
            session.commit() 

    def check_expired(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            Coinflip.clear_expired_coinflips(self)
            return func(self, *args, **kwargs)
        return wrapper

    @check_expired
    def get_public_cf(self) -> Status:
        with self.session() as session:
            cfs: List["Coinflip.CoinflipData"] = (
                session.query(Coinflip.CoinflipData).filter_by(opponent_id=None).all()
            )
            if cfs:
                return Status(status=True, body=cfs)
            return Status(message="No public coinflips found")

    @usercheck
    @check_expired
    def self_coinflip(self, discord_id: int, amount: int) -> Status:
        c: Status = User.check_balance(self,discord_id, amount, "self")
        if not c.status:
            return c
        
        stats: CoinflipStats = User.get_stats(self, discord_id, CoinflipStats)

        cf_res: Status = self.coinflip(requester_id=discord_id, req_loss_streak=stats.loss_streak, amount=amount)

        winner: int = cf_res.body["winner"] # discord_id or 0

        stats.modify(
            games_won=1 if winner else 0,
            games_lost=1 if not winner else 0,
            money_won=amount if winner == discord_id else 0,
            money_lost=-amount if not winner else 0,
            most_lost=amount if not winner else 0,
            most_lost_to_id=discord_id if not winner else 0,
            loss_streak=0 if winner else stats.loss_streak + 1
        )

        User.set_stats(self, discord_id, CoinflipStats, stats)

        User.modify_balance(self, discord_id, amount if winner else -amount)

        return cf_res

    @usercheck("opponent_id")
    @check_expired
    def make_coinflip(self, discord_id: int, opponent_id: int | None, amount: int) -> Status:
        if discord_id == opponent_id:
            return Check.USER_SAME_ID.to_status()
        
        c: Status = User.check_balance(self,discord_id, amount)
        if not c.status:
            return Check.USER_BAL_SELF.to_status()
        
        c: Status = User.check_balance(self, opponent_id, amount, "other")
        if not c.status:
            return Check.USER_BAL_OTHER.to_status()

        if self.get_coinflip_by_users(discord_id, opponent_id).status:
            return Check.CF_EXISTS.to_status()

        return self.create_coinflip(discord_id, opponent_id, amount)

    @usercheck("opponent_id")
    @check_expired
    def accept_coinflip(self, discord_id: int, opponent_id: int | None, id: str | None) -> Status:
        if discord_id == opponent_id:
            return Check.USER_SAME_ID.to_status()

        res: Status = self.get_coinflip_by_users(discord_id, opponent_id) if opponent_id else self.get_coinflip(id)

        if not res.status:
            return Check.CF_NOT_EXISTS.to_status()

        cf: Coinflip.CoinflipData = res.body

        c: Status = User.check_balance(self, discord_id, cf.amount)
        if not c.status:
            return c
        
        c: Status = User.check_balance(self, opponent_id, cf.amount, "other")
        if not c.status:
            return c

        if cf.requester_id == discord_id:
            return Check.CF_REQUEST_NOT_YOURS.to_status()

        req_stats: CoinflipStats = User.get_stats(self, cf.requester_id, CoinflipStats)
        opp_stats: CoinflipStats = User.get_stats(self, cf.opponent_id, CoinflipStats)

        cf_res: Status = self.coinflip(cf.requester_id, 0, cf.opponent_id, 0, cf.amount)

        # update stats, coinflip always returns true
        winner = cf_res.body["winner"]
        loser = cf_res.body["loser"]
        req_stats.modify(
            games_won=1 if winner == cf.requester_id else 0,
            games_lost=1 if loser == cf.requester_id else 0,
            money_won=cf.amount if winner == cf.requester_id else 0,
            money_lost=-cf.amount if loser == cf.requester_id else 0,
            most_lost=cf.amount if loser == cf.requester_id else 0,
            most_lost_to_id=cf.opponent_id if loser == cf.requester_id else 0,
            loss_streak=req_stats.loss_streak
        )
        
        opp_stats.modify(
            games_won=1 if winner == cf.opponent_id else 0,
            games_lost=1 if loser == cf.opponent_id else 0,
            money_won=cf.amount if winner == cf.opponent_id else 0,
            money_lost=-cf.amount if loser == cf.opponent_id else 0,
            most_lost=cf.amount if loser == cf.opponent_id else 0,
            most_lost_to_id=cf.requester_id if loser == cf.opponent_id else 0,
            loss_streak=opp_stats.loss_streak
        )

        User.set_stats(self, cf.requester_id, CoinflipStats, req_stats)
        User.set_stats(self, cf.opponent_id, CoinflipStats, opp_stats)

        User.modify_balance(self, winner, cf.amount)
        User.modify_balance(self, loser, -cf.amount)

        self.delete_coinflip(cf.id)

        return cf_res

    