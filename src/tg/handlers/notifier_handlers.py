from aiogram import types
from aiogram.dispatcher import FSMContext

from src.tg.tsdp import dp
from src.tg.states import StartState, NotifierState, ExplorerState
from src.tg.keyboards import my_subscriptions_kb, account_kb, market_kb, back_kb
from src.db_utils.queries import get_user_subscriptions, allow_to_add_new_subscription, unsubscribe_from, \
    subscribe_to
from src.bitshares_utils.base import get_account, get_market, get_new_price, get_last_op
from src.text_content import TextMessage, ButtonText, CallBackCommands
from src.tg.messages_processing import gen_new_view
from config import cfg, PRICE_CHANGE_PERC


@dp.message_handler(lambda message: message.text in ButtonText.notifier_buttons_text, state=StartState.notifier)
async def notifier_menu_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if message.text == ButtonText.my_subscriptions:
        async with dp.bot.db.acquire() as conn:
            subscriptions = await get_user_subscriptions(conn, message.chat.id)
        if subscriptions:
            reply = TextMessage.notifier_answers[message.text]
            temp_msg = await dp.bot.safe_send_message(text=TextMessage.request_processing, chat_id=message.chat.id,
                                                 reply_markup=back_kb)
            if temp_msg:
                _kb = await my_subscriptions_kb(subscriptions)
                new_state = NotifierState.my_subscriptions
        else:
            reply = TextMessage.notifier_answers['no_subscriptions']
            _kb = back_kb
            new_state = StartState.notifier

    await new_state.set()
    _new_msg = await dp.bot.safe_send_message(text=reply, chat_id=message.chat.id, reply_markup=_kb)
    await state.set_data({"current_frame_msg_id": _new_msg.message_id})


@dp.callback_query_handler(lambda call: call.data.split()[0] == CallBackCommands.explore, state="*")
async def to_explorer_call_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    bts_object = call.data.split()[1]

    if '/' in bts_object:
        bts_object_type = "market"
        await ExplorerState.markets.set()
    else:
        await ExplorerState.accounts.set()
        bts_object_type = "account"

    new_msg = await gen_new_view(call, bts_object_type)

    if user_data.get("current_frame_msg_id"):
        await dp.bot.safe_delete_message(message_id=user_data["current_frame_msg_id"], chat_id=call.from_user.id)

    await state.set_data({"current_frame_msg_id": new_msg.message_id})


@dp.callback_query_handler(lambda _: cfg['plugins']['notifier'],
                           lambda call: call.data.split()[0] in (
                           CallBackCommands.subscribe, CallBackCommands.unsubscribe, CallBackCommands.to_subs),
                           state="*")
async def explorer_notifier_features_call_handler(call: types.CallbackQuery, state: FSMContext):
    call_data_list = call.data.split()
    command, object_str = call_data_list[0], call_data_list[1]
    call_answer_text = None
    alert = False
    is_subscribed = False

    if command == CallBackCommands.to_subs:
        async with dp.bot.db.acquire() as conn:
            subscriptions = await get_user_subscriptions(conn, call.from_user.id)
        edited_reply = TextMessage.notifier_my_subscriptions
        kb = await my_subscriptions_kb(subscriptions)
        await NotifierState.my_subscriptions.set()

    if command in (CallBackCommands.subscribe, CallBackCommands.unsubscribe):
        alert = True
        subs_kwargs = {"telegram_user_id": call.from_user.id}

        if object_str[2] == '2':
            bts_object = await get_account(object_str)
            subs_kwargs["bts_object"] = bts_object.identifier
            subs_kwargs["last_op"] = await get_last_op(bts_object)
            kb_func = account_kb
            object_name = bts_object.name

        elif '/' in object_str:
            subs_kwargs["bts_object"] = object_str
            subs_kwargs["last_price"] = await get_new_price(object_str)
            subs_kwargs['price_change_percent'] = PRICE_CHANGE_PERC
            kb_func = market_kb
            object_name = object_str

        if command == CallBackCommands.subscribe:
            async with dp.bot.db.acquire() as conn:
                is_allow = await allow_to_add_new_subscription(conn, call.from_user.id)
            if is_allow:
                async with dp.bot.db.acquire() as conn:
                    is_subscribed = await subscribe_to(conn, **subs_kwargs)
                if is_subscribed:
                    if '/' in object_str:
                        call_answer_text = TextMessage.successfully_subscribed_market.format(object_name)
                    else:
                        call_answer_text = TextMessage.successfully_subscribed_account.format(object_name)
            else:
                call_answer_text = TextMessage.no_enought_limit

        elif command == CallBackCommands.unsubscribe:
            async with dp.bot.db.acquire() as conn:
                await unsubscribe_from(conn, call.from_user.id, object_str)
            if '/' in object_str:
                async with dp.bot.db.acquire() as conn:
                    await unsubscribe_from(conn, call.from_user.id, f"{object_str.split('/')[1]}/{object_str.split('/')[0]}")
            call_answer_text = TextMessage.successfully_unsubscribed.format(object_name)

        edited_reply = None
        kb = kb_func(object_str, is_subscribed=is_subscribed)

    if call_answer_text:
        await dp.bot.answer_callback_query(call.id,
                                           text=call_answer_text,
                                           show_alert=alert)

    await dp.bot.safe_edit_message(call.message.message_id,
                                   text=edited_reply,
                                   chat_id=call.from_user.id,
                                   reply_markup=kb)
