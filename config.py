import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('TOKEN')
        self.DB_URL = os.getenv('DB_URL')
        self.ENABLE_DMS = os.getenv('ENABLE_DMS') == 'true'
        self.MAX_LOSS_STREAK = int(os.getenv('MAX_LOSS_STREAK'))
        self.STREAK_BIAS = float(os.getenv('STREAK_BIAS'))
        self.BASE_ODDS = int(os.getenv('BASE_ODDS'))
        print(self.ENABLE_DMS)

        self.permission_whitelist_uids: list[int] = [1209228744921710664]
        self.bot_channel: int = int(os.getenv('BOT_CHANNEL'))
