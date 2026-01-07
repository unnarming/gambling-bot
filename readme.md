# .env setup

Create a `.env` file in the root directory with the following variables:

## Required Environment Variables

### Discord Bot Configuration
- `TOKEN` - Your Discord bot token (required)
- `ENABLE_DMS` - Enable/disable DMs (set to `true` or `false`)
- `PERM_USERS` - Comma-separated list of Discord user IDs that have permission to use admin commands (e.g., `123456789,987654321`)
- `BOT_CHANNEL` - The Discord channel ID where bot commands should be used (integer)

### Database Configuration
- `DB_URL` - Database connection URL (e.g., `sqlite:///gambling_bot.db` or your database connection string)

### Coinflip Game Configuration
- `MAX_LOSS_STREAK` - Maximum loss streak before bias adjustment (integer)
- `STREAK_BIAS` - Bias multiplier applied after max loss streak (float, e.g., `1.5`)
- `BASE_ODDS` - Base odds percentage for coinflip games (integer, e.g., `50` for 50/50)

## Example .env File
```
TOKEN=your_discord_bot_token_here
ENABLE_DMS=true
PERM_USERS=123456789,987654321
BOT_CHANNEL=123456789012345678
DB_URL=sqlite:///gambling_bot.db
MAX_LOSS_STREAK=5
STREAK_BIAS=1.5
BASE_ODDS=50
```