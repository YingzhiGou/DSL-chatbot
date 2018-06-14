# local config
# for the ChatterBot bot
import os

# get everything from base config file
BASE_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "errbot-config.py")
exec(compile(
    open(BASE_CONFIG_PATH, "rb").read(), BASE_CONFIG_PATH, 'exec'), globals(), locals()
)
del BASE_CONFIG_PATH

# modify
BOT_LOG_LEVEL = logging.INFO

CHATROOM_FN = 'Dora the Bot'
BOT_ALT_PREFIXES = ('Dora',)

BOT_DATA_DIR = os.path.join(ERRBOT_ROOT, 'data')
if not os.path.isdir(BOT_DATA_DIR):
    os.mkdir(BOT_DATA_DIR)
