import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('TOKEN')
        self.ENABLE_DMS = os.getenv('ENABLE_DMS').lower() == 'true'
        self.PERMISSION_WHITELIST_UIDS: list[int] = os.getenv('PERM_USERS').split(',')
        self.BOT_CHANNEL: int = int(os.getenv('BOT_CHANNEL'))
        
        self.DB_URL = os.getenv('DB_URL')
        
        self.MAX_LOSS_STREAK = int(os.getenv('MAX_LOSS_STREAK'))
        self.STREAK_BIAS = float(os.getenv('STREAK_BIAS'))
        self.BASE_ODDS = int(os.getenv('BASE_ODDS'))
