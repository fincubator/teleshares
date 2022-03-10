from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.tg.tsbot import TeleSharesBot
from config import cfg


storage = RedisStorage2()
bot = TeleSharesBot(**cfg['telegram'])
dp = Dispatcher(bot, storage=storage)


from src.tg.handlers.admin_handlers import *
from src.tg.handlers.start_handlers import *
from src.tg.handlers.explorer_handlers import *


for plugin, state in cfg['plugins'].items():
    setattr(dp, plugin, state)

if dp.wallet:
    from src.tg.handlers.wallet_handlers import *
if dp.notifier:
    from src.tg.handlers.notifier_handlers import *
if dp.gateways:
    from src.tg.handlers.gateways_handlers import *
