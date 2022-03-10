from aiogram import types
from aiogram.utils.markdown import hbold
from aiogram.dispatcher import FSMContext

from src.tg.tsdp import dp
from src.tg.states import WalletState, StartState, states_groups
from src.bitshares_utils.base import broadcast, set_default_account, get_default_account
from src.text_content import TextMessage, CallBackCommands

from config import cfg


@dp.message_handler(state=StartState.wallet, user_id=[cfg['telegram']['root_id']])
async def wallet_account_select_handler(message: types.Message):

    set_default_account(message.text)
    current_default_account = hbold(get_default_account())
    await dp.bot.safe_send_message(text=TextMessage.default_account_change.format(current_default_account),
                                   chat_id=message.chat.id)


@dp.callback_query_handler(state=WalletState.operation_build, user_id=[cfg['telegram']['root_id']])
async def wallet_operation_build_callback_handler(call: types.CallbackQuery, state: FSMContext):
    call_data_split = call.data.split()
    command = call_data_split[0]
    user_data = await state.get_data()

    if command == CallBackCommands.destroy:
        await clear_operation_cache(user_data)
        await dp.bot.safe_delete_message(message_id=call.message.message_id,
                                         chat_id=call.from_user.id)

    if command == CallBackCommands.broadcast:
        op_body = user_data["operation"]
        broadcasting_result = await broadcast(**op_body)
        if issubclass(broadcasting_result.__class__, Exception):
            await dp.bot.answer_callback_query(call.id,
                                               text=TextMessage.failed_to_broadcast.format(str(broadcasting_result)),
                                               show_alert=True)
        else:
            await dp.bot.safe_send_message(text=TextMessage.broadcast.format(broadcasting_result),
                                           chat_id=call.from_user.id)
            await dp.bot.safe_delete_message(message_id=call.message.message_id,
                                             chat_id=call.from_user.id)

            await clear_operation_cache(user_data)

    await state.set_data(user_data)


async def clear_operation_cache(user_data):
    previous_state = user_data["previous_state"]
    for group in states_groups:
        for _state in group.states:
            if previous_state == _state.state:
                await _state.set()
                break
    for i in ("current_op_msg", "operation", "await_for_param", "set_message", "previous_state"):
        try:
            user_data.pop(i)
        except KeyError:
            continue
