from aiogram.utils import executor

from src.tg.tsdp import dp
from src.bitshares_utils.notifier_utils import notifier_loop


# Say hi to root telegram account
dp.bot.loop.create_task(dp.bot.root_greeting())

if dp.notifier:
    dp.bot.loop.create_task(notifier_loop(bot=dp.bot))


executor.start_polling(dp)
