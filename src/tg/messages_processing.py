from aiogram.types import Message, CallbackQuery

from src.tg.tsdp import dp
from src.tg.keyboards import market_kb, account_kb, back_kb
from src.db_utils.queries import is_subscribed_to
from src.text_content import TextMessage
from src.bitshares_utils.base import get_account, get_market
from src.bitshares_utils.views import get_account_info_frame_data, account_view, market_view


async def gen_new_view(message: Message or CallbackQuery, bts_object_type) -> Message:
    """
    Generate telegram message with BitShares object view and send it to user
    :return: Message
    """
    kb = None
    reply = None

    if isinstance(message, Message):
        user_input = message.text
    else:
        user_input = message.data.split()[1]

    # This messages is needed because Telegram don't allow to attach Keyboard and InlineKeyboard in one message
    temp_msg = await dp.bot.safe_send_message(text=TextMessage.request_processing, chat_id=message.from_user.id,
                                              reply_markup=back_kb)

    if temp_msg:

        if bts_object_type == "account":

            _account = await get_account(user_input)
            if not _account:
                reply = TextMessage.no_account.format(user_input)
            else:
                frame_data = await get_account_info_frame_data(_account)
                reply = await account_view(_account.name,
                                           frame_data=frame_data)

                async with dp.bot.db.acquire() as conn:
                    is_subscribed = await is_subscribed_to(conn, message.from_user.id, _account['id'])

                kb = account_kb(_account['id'],
                                is_subscribed=is_subscribed)

        if bts_object_type == "market":

            _market = await get_market(user_input)
            if not _market:
                reply = TextMessage.bad_market
            else:
                _market_name = f"{_market['quote'].symbol}/{_market['base'].symbol}"
                frame_data = await _market.ticker()

                async with dp.bot.db.acquire() as conn:
                    is_subscribed = await is_subscribed_to(conn, message.from_user.id,
                                                           _market_name)
                reply = await market_view(_market_name,
                                          frame_data=frame_data)
                kb = market_kb(_market_name,
                               is_subscribed=is_subscribed)

        return await dp.bot.safe_send_message(text=reply, chat_id=message.from_user.id, reply_markup=kb)
