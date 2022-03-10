import asyncio
import logging

from src.db_utils.queries import get_all_subscriptions, set_new_op, set_new_price
from src.bitshares_utils.base import get_new_ops, get_new_price
from src.bitshares_utils.views import format_op, retrieve_market_name_from_op
from src.tg.keyboards import notification_kb

from src.text_content import SystemLogs, BtsObjectRepr


logger = logging.getLogger(__name__)
logger.debug(SystemLogs.start_history_parser)


async def notifier_loop(bot) -> None:
    """
    Main loop of the notifier plugin.
    Automatically append to bot's event_loop
    """

    while True:
        async with bot.db.acquire() as conn:

            subs = await get_all_subscriptions(conn)

        for s in subs:

            # Accounts parsing
            if s.bts_object[2] == "2":
                new_ops = await get_new_ops(s.bts_object, s.last_op)
                if new_ops:

                    # If received some new operations,
                    # first updating user account subscription with id of newest operation
                    async with bot.db.acquire() as conn:
                        await set_new_op(conn, s.id, new_ops[0]['id'].split('.')[2])

                    # BitShares account history received in order newest->older
                    # Need to reverse ops list
                    acc_hist = reversed(new_ops)

                    for op in acc_hist:
                        notification = await format_op(op, s.bts_object)

                        # if operation contains Price object, add invert button to it.
                        if op['op'][0] in (1, 4):
                            op_market = await retrieve_market_name_from_op(op)
                            kb = await notification_kb(account=s.bts_object, market=op_market, invertible=True)
                        else:
                            kb = await notification_kb(account=s.bts_object)

                        await send_notification(bot, notification, s.telegram_user_id, kb)

            # Markets parsing
            if '/' in s.bts_object:
                new_price = await get_new_price(s.bts_object)
                old_price = float(s.last_price)

                if new_price != old_price:
                    change = round(
                        ((new_price - old_price) / old_price) * 100,
                        2)
                    if abs(change) > float(s.price_change_percent):
                        async with bot.db.acquire() as conn:
                            await set_new_price(conn, s.id, new_price)

                        if change > 0:
                            change = f"📈 {change}"
                        elif change < 0:
                            change = f"📉{change}"

                        notification = BtsObjectRepr.price_change.format(s.bts_object, new_price, change)
                        kb = await notification_kb(market=s.bts_object)

                        await send_notification(bot, notification, s.telegram_user_id, kb)

        await asyncio.sleep(3)


async def send_notification(bot, notification, chat_id, kb):
    await bot.safe_send_message(text=notification, chat_id=chat_id, reply_markup=kb)
