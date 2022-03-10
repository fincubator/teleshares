from aiogram import types
from aiogram.utils.markdown import hbold

from src.tg.tsdp import dp
from src.tg.states import StartState, GatewaysState
from src.tg.keyboards import gateway_kb, back_kb
from src.bitshares_utils.views import gateway_view
from src.text_content import TextMessage

from config import gateways_info


@dp.message_handler(state=StartState.gateways)
async def gateways_menu_handler(message: types.Message):

    temp_msg = await dp.bot.safe_send_message(text=TextMessage.request_processing, chat_id=message.chat.id,
                                              reply_markup=back_kb)
    if temp_msg:
        if message.text in gateways_info.keys():
            reply = await gateway_view(gateways_info[message.text])
            _kb = gateway_kb(gateways_info[message.text])
        else:
            reply = TextMessage.no_gateways.format(hbold(message.text))
            _kb = None
        await GatewaysState.main.set()
        await dp.bot.safe_send_message(text=reply, chat_id=message.chat.id, reply_markup=_kb)
