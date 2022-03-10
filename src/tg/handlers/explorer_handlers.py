import textwrap

from aiogram import types
from aiogram.dispatcher import FSMContext

from src.tg.tsdp import dp
from src.tg.states import StartState, ExplorerState
from src.tg.keyboards import keyboards, market_kb, account_kb
from src.tg.messages_processing import gen_new_view

from src.bitshares_utils.views import *
from src.db_utils.queries import is_subscribed_to

from config import VIEW_ASSETS_IN_BALANCE, VIEW_OP_LIMIT, VIEW_ORDERS_IN_BOOK, VIEW_OPENORDERS_LIMIT


@dp.message_handler(lambda message: message.text in ButtonText.explorer_buttons_text, state=StartState.explorer)
async def explorer_menu_handler(message: types.Message):
    new_state = None
    reply = TextMessage.explorer_answers.get(message.text)

    if message.text == ButtonText.accounts:
        new_state = ExplorerState.accounts

    if message.text == ButtonText.markets:
        new_state = ExplorerState.markets

    if message.text == ButtonText.fee_schedule:
        new_state = ExplorerState.fee_schedule
        reply += await fee_schedule_view()

    await dp.bot.safe_send_message(text=reply, chat_id=message.chat.id, reply_markup=keyboards[message.text])
    await new_state.set()


@dp.message_handler(state=ExplorerState)
async def bitshares_object_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == ExplorerState.accounts.state:
        bts_object_type = "account"
    if current_state == ExplorerState.markets.state:
        bts_object_type = "market"

    new_msg = await gen_new_view(message, bts_object_type)

    user_data = await state.get_data()
    if user_data.get("current_frame_msg_id"):
        await dp.bot.safe_delete_message(message_id=user_data["current_frame_msg_id"], chat_id=message.chat.id)
    await state.set_data({"current_frame_msg_id": new_msg.message_id})


@dp.callback_query_handler(lambda call: call.data.split()[0] in CallBackCommands.frames_commands, state=ExplorerState)
async def explorer_frame_call_handler(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    call_data_list = call.data.split()
    command, object_str = call_data_list[0], call_data_list[1]

    try:
        pag_data = {call_data_list[2].split(':')[0]: call_data_list[2].split(':')[1]}
    except IndexError:
        pag_data = {}

    frame_data = list()
    right_data = None
    left_data = None
    view = None
    kb_func = None
    call_answer_text = str()
    need_alert = False

    async with dp.bot.db.acquire() as conn:
        is_subscribed = await is_subscribed_to(conn, call.from_user.id, object_str)

    if current_state == ExplorerState.accounts.state:
        view = account_view
        kb_func = account_kb
        _account = await get_account(object_str)
        object_name = _account.name

        if command == CallBackCommands.info:
            frame_data = await get_account_info_frame_data(_account.name)
            if _account.is_ltm:
                frame_data.append(('ltm', BtsObjectRepr.ltm))

        if command == CallBackCommands.balances:
            _balances = await _account.balances
            if _balances:
                _assets = [(await i.asset) for i in _balances]

                if not pag_data:
                    frame_data = _balances[0:VIEW_ASSETS_IN_BALANCE]
                elif pag_data.get('right'):
                    frame_data = []
                    for _b in _balances:
                        _asset = await _b.asset
                        if int(_asset.identifier.split('.')[2]) > int(pag_data['right']):
                            frame_data.append(_b)
                    frame_data = frame_data[0:VIEW_ASSETS_IN_BALANCE]

                elif pag_data.get('left'):
                    frame_data = []
                    for _b in _balances:
                        _asset = await _b.asset
                        if int(_asset.identifier.split('.')[2]) < int(pag_data['left']):
                            frame_data.append(_b)
                    frame_data = frame_data[-VIEW_ASSETS_IN_BALANCE:]

                right_data = None \
                    if (_assets[-1]).identifier.split('.')[2] == (await frame_data[-1].asset).identifier.split('.')[2] \
                    else (await frame_data[-1].asset).identifier.split('.')[2]
                left_data = None \
                    if (_assets[0]).identifier.split('.')[2] == (await frame_data[0].asset).identifier.split('.')[2] \
                    else (await frame_data[0].asset).identifier.split('.')[2]

        if command == CallBackCommands.history:
            _full_history = await get_new_ops(_account)
            if pag_data:
                if pag_data.get('right'):
                    frame_data = list(
                        filter(
                            lambda i: int(i['id'].split('.')[2]) < int(pag_data['right']),
                            _full_history
                        )
                    )[0:VIEW_OP_LIMIT]

                if pag_data.get('left'):
                    frame_data = list(
                        filter(
                            lambda i: int(i['id'].split('.')[2]) > int(pag_data['left']),
                            _full_history
                        )
                    )[-VIEW_OP_LIMIT:]

            else:
                frame_data = [i for i in _full_history[0:VIEW_OP_LIMIT]]

            right_data = None if _full_history[-1]['id'] == frame_data[-1]['id'] else frame_data[-1]['id'].split('.')[2]
            left_data = None if _full_history[0]['id'] == frame_data[0]['id'] else frame_data[0]['id'].split('.')[2]

        if command == CallBackCommands.openorders:
            orders = await _account.openorders
            if not orders:
                frame_data = TextMessage.no_account_openorders.format(object_name)
            else:
                orders.sort(reverse=True, key=lambda i: i['id'])

                if pag_data:
                    if pag_data.get('right'):
                        frame_data = list(
                            filter(
                                lambda i: int(i['id'].split('.')[2]) < int(pag_data['right']),
                                orders
                            )
                        )[0:VIEW_OPENORDERS_LIMIT]

                    if pag_data.get('left'):
                        frame_data = list(
                            filter(
                                lambda i: int(i['id'].split('.')[2]) > int(pag_data['left']),
                                orders
                            )
                        )[-VIEW_OPENORDERS_LIMIT:]
                else:
                    frame_data = [i for i in orders[0:VIEW_OPENORDERS_LIMIT]]

                right_data = None if orders[-1]['id'] == frame_data[-1]['id'] else frame_data[-1]['id'].split('.')[2]
                left_data = None if orders[0]['id'] == frame_data[0]['id'] else frame_data[0]['id'].split('.')[2]

    if current_state in ExplorerState.markets.state:
        view = market_view
        kb_func = market_kb
        _market = await get_market(object_str)
        object_name = object_str

        if command == CallBackCommands.ticker:
            frame_data = await _market.ticker()

        if command == CallBackCommands.trades:
            trades = []
            async for t in _market.trades():
                trades.append(t)

            if not trades:
                frame_data = TextMessage.no_trades_on_market
            else:
                if not pag_data:
                    frame_data = trades[0:VIEW_OPENORDERS_LIMIT]
                else:
                    if pag_data.get('right'):
                        frame_data = list(
                            filter(
                                lambda i: i['sequence'] < int(pag_data['right']),
                                trades
                            )
                        )[0:VIEW_OPENORDERS_LIMIT]

                    if pag_data.get('left'):
                        frame_data = list(
                            filter(
                                lambda i: i['sequence'] > int(pag_data['left']),
                                trades
                            )
                        )[-VIEW_OPENORDERS_LIMIT:]

                right_data = None if trades[-1]['sequence'] == frame_data[-1]['sequence'] else frame_data[-1]['sequence']
                left_data = None if trades[0]['sequence'] == frame_data[0]['sequence'] else frame_data[0]['sequence']

        if command in (CallBackCommands.asks, CallBackCommands.bids):
            call_answer_text = TextMessage.experimental_feature

            orderbook = await _market.orderbook()

            if command == CallBackCommands.asks:
                right_compare = lambda i: i['price'] > float(pag_data['right'])
                left_compare = lambda i: i['price'] < float(pag_data['left'])
                orderbook = orderbook['asks']
                trade_word = "Sell"

            if command == CallBackCommands.bids:
                right_compare = lambda i: i['price'] < float(pag_data['right'])
                left_compare = lambda i: i['price'] > float(pag_data['left'])
                orderbook = orderbook['bids']
                trade_word = "Buy"

            if not orderbook:
                frame_data = TextMessage.no_orders_on_market.format(command)

            else:
                if pag_data:
                    if pag_data.get('right'):
                        frame_data = [i for i in orderbook if right_compare(i)][0:VIEW_ORDERS_IN_BOOK]
                    if pag_data.get('left'):
                        frame_data = [i for i in orderbook if left_compare(i)][-VIEW_ORDERS_IN_BOOK:]
                else:
                    frame_data = orderbook[0:VIEW_ORDERS_IN_BOOK]

                right_data = None if orderbook[-1]['price'] == frame_data[-1]['price'] else frame_data[-1]['price']
                left_data = None if orderbook[0]['price'] == frame_data[0]['price'] else frame_data[0]['price']

                frame_data.insert(0, f"{ textwrap.fill(trade_word + ' ' + object_name.split('/')[0], 10)}")

    pag_data = {
        "command": command,
        "right": right_data,
        "left": left_data
    }

    title = command.capitalize().replace("_", " ")

    edited_reply = await view(object_name, title=title, frame=command, frame_data=frame_data)

    kb = kb_func(object_str, is_subscribed, pag_data=pag_data)

    # TODO catch alert exceptions
    if call_answer_text:
        await dp.bot.answer_callback_query(call.id,
                                           text=call_answer_text,
                                           show_alert=need_alert)

    await dp.bot.safe_edit_message(call.message.message_id,
                                   text=edited_reply,
                                   chat_id=call.from_user.id,
                                   reply_markup=kb)
