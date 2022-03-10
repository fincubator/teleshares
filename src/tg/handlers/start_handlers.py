from aiogram import types
from aiogram.utils.markdown import hcode, hbold
from aiogram.dispatcher import FSMContext

from src.tg.tsdp import dp
from src.tg.keyboards import start_kb, explorer_kb, notifier_kb, gateways_kb, wallet_kb, to_git_kb, operation_build_kb
from src.tg.states import StartState, ExplorerState, NotifierState, GatewaysState, WalletState
from src.text_content import TextMessage, ButtonText, CallBackCommands
from src.bitshares_utils.base import parse_operation, get_default_account
from src.db_utils.queries import add_telegram_user
from src.bitshares_utils.views import invert_price_in_message

from config import cfg


op_commands = ('transfer', 'sell', 'buy', 'cancel')


@dp.message_handler(lambda _: cfg['plugins']['wallet'],
                    commands=[*op_commands],
                    state='*',
                    user_id=[cfg['telegram']['root_id']])
async def wallet_operation_build_handler(message: types.Message, state: FSMContext):
    message_split = message.text.split()
    command = message.text.split()[0].replace('/', '')
    if len(message_split) == 1:
        await dp.bot.safe_send_message(text=TextMessage.operations_hints[command], chat_id=message.chat.id)
    # TODO destroy op button
    else:
        op_text = message.text.replace(f"/{command} ", '')
        op_body = await parse_operation(op_text, command)

        if isinstance(op_body, dict):
            reply = get_default_account() + '\n' + TextMessage.operations_build[command] + "\n\n"
            for k, v in op_body.items():
                # TODO state set
                if k != "op_type":
                    reply += f"{hbold(k)}: {v}\n\n"

            user_data = await state.get_data()
            current_state = await state.get_state()

            user_data["operation"] = op_body
            if current_state != WalletState.operation_build.state:
                user_data["previous_state"] = current_state

            kb = operation_build_kb(op_body["op_type"])

            msg = await dp.bot.safe_send_message(text=reply, chat_id=message.chat.id, reply_markup=kb)
            if user_data.get("current_op_msg"):
                await dp.bot.safe_delete_message(message_id=user_data["current_op_msg"], chat_id=message.chat.id)
            user_data["current_op_msg"] = msg.message_id

            await WalletState.operation_build.set()
            await state.set_data(user_data)

        else:
            await dp.bot.safe_send_message(text=TextMessage.bad_operation.format(command), chat_id=message.chat.id)


@dp.callback_query_handler(lambda call: call.data.split()[0] == CallBackCommands.invert, state='*')
async def price_invert_handler(call: types.CallbackQuery):
    bts_object = call.data.split()[1]

    new_bts_object = f"{bts_object.split('/')[1]}/{bts_object.split('/')[0]}"
    edited_reply = await invert_price_in_message(call.message.html_text)
    kb = call.message.reply_markup

    for i in kb.inline_keyboard:
        command, _bts_object = i[0]["callback_data"].split()

        if command == CallBackCommands.invert:
            i[0]["callback_data"] = f"{CallBackCommands.invert} {new_bts_object}"
        if command == CallBackCommands.explore and bts_object == _bts_object:
            i[0]["text"] = f"📊{new_bts_object}"
            i[0]["callback_data"] = f"{CallBackCommands.explore} {new_bts_object}"

    await dp.bot.safe_edit_message(message_id=call.message.message_id,
                                   text=edited_reply,
                                   chat_id=call.from_user.id,
                                   reply_markup=kb)


@dp.message_handler(lambda message: message.text == ButtonText.back, state="*")
async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    user_data = await state.get_data()

    if user_data.get("current_frame_msg_id"):
        await dp.bot.safe_delete_message(message_id=user_data["current_frame_msg_id"], chat_id=message.chat.id)
        user_data.pop("current_frame_msg_id")

    # By default return to start menu
    new_state = StartState.start
    answer = TextMessage.start
    kb = start_kb

    if current_state in ExplorerState.states_names:
        new_state = StartState.explorer
        answer = TextMessage.explorer
        kb = explorer_kb

    if current_state in NotifierState.states_names:
        new_state = StartState.notifier
        answer = TextMessage.notifier
        kb = notifier_kb

    if current_state in GatewaysState.states_names:
        new_state = StartState.gateways
        answer = TextMessage.gateways
        kb = gateways_kb()

    if current_state in WalletState.states_names:
        new_state = StartState.wallet
        answer = TextMessage.wallet
        kb = wallet_kb
        if current_state == WalletState.operation_build.state:
            try:
                user_data.pop("operation")
            except:
                pass

    await dp.bot.safe_send_message(text=answer,
                                   chat_id=message.chat.id,
                                   reply_markup=kb)
    await new_state.set()
    await state.set_data(user_data)


@dp.message_handler(commands=["start", "restart"], state="*")
async def start_and_restart_handler(message: types.Message):
    async with dp.bot.db.acquire() as conn:
        await add_telegram_user(conn, **dict(message.from_user))
    await StartState.start.set()
    await dp.bot.safe_send_message(text=TextMessage.start, chat_id=message.chat.id, reply_markup=start_kb)


@dp.message_handler(lambda message: message.text in ButtonText.start_buttons_text, state=StartState.start)
async def start_menu_handler(message: types.Message):
    new_state = StartState.start
    kb = start_kb
    reply = ""
    if message.text == ButtonText.explorer:
        reply = TextMessage.explorer
        kb = explorer_kb
        new_state = StartState.explorer

    if message.text == ButtonText.donate:
        reply = TextMessage.donate
        for k, v in cfg["donate_addresses"].items():
            reply += f"{hbold(k)}:\n {hcode(v)}\n\n"
            kb = start_kb

    if message.text == ButtonText.notifier:
        if dp.notifier:
            reply = TextMessage.notifier
            kb = notifier_kb
            new_state = StartState.notifier
        else:
            reply = TextMessage.plugin_disabled.format(message.text)

    if message.text == ButtonText.wallet:
        if dp.wallet:
            if message.chat.id != cfg['telegram']['root_id']:
                reply = TextMessage.wallet_not_in_root
                kb = to_git_kb
            else:
                current_default_account = hbold(get_default_account())
                reply = TextMessage.wallet.format(current_default_account)
                kb = wallet_kb
                new_state = StartState.wallet
        else:
            reply = TextMessage.plugin_disabled.format(message.text)

    if message.text == ButtonText.gateways:
        if dp.gateways:
            reply = TextMessage.gateways
            kb = gateways_kb()
            new_state = StartState.gateways
        else:
            reply = TextMessage.plugin_disabled.format(message.text)

    await new_state.set()
    await dp.bot.safe_send_message(text=reply, chat_id=message.chat.id, reply_markup=kb)
