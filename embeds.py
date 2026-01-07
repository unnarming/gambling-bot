import discord
from utils import Status
from config import Config

class Embeds:
    def __init__(self, config: Config):
        self.config = config

    def error(self, message: str) -> discord.Embed:
        return discord.Embed(colour=discord.Colour.red()).add_field(name="Error", value=message, inline=False)

    def status(self, status: Status) -> discord.Embed:
        if status.status:
            return discord.Embed(colour=discord.Colour.green()).add_field(name="Success", value=status.message, inline=False)
        else:
            return discord.Embed(colour=discord.Colour.red()).add_field(name="Error", value=status.message, inline=False)
    
    def success(self, message: str) -> discord.Embed:
        return discord.Embed(colour=discord.Colour.green()).add_field(name="Success", value=message, inline=False)

    color_enum = {
        "success": discord.Colour.green(),
        "error": discord.Colour.red(),
        "info": discord.Colour.blurple(),
        "warning": discord.Colour.yellow(),
        "neutral": discord.Colour.light_grey(),
    }

    def base(self, title: str = "", description: str = "", color: str = "neutral") -> discord.Embed:
        return discord.Embed(colour=self.color_enum[color]).add_field(name=title, value=description, inline=False)

    def stats(self, *stats: tuple[str, str], title: str = "") -> discord.Embed:
        embed: discord.Embed = self.base(title=title, color="neutral")
        for stat in stats:
            embed.add_field(name=stat[0], value=stat[1], inline=True)
        return embed