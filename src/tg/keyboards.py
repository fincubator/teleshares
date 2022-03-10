from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from src.bitshares_utils.base import get_account
from src.tg.buttons import *
from src.tg.tsdp import dp
from src.text_content import CallBackCommands

from config import gateways_info, cfg, wallet_data, SOURCE_CODE_URL

back_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(back_bt)

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.row(explorer_bt, notifier_bt)
start_kb.row(gateways_bt, wallet_bt)
start_kb.row(donate_bt)

explorer_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for b in (explore_accounts_bt, explore_markets_bt, explore_fee_schedule_bt, back_bt):
    explorer_kb.row(b)

notifier_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for b in (notifier_my_subscriptions_bt, back_bt):
    notifier_kb.row(b)

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.row(admin_get_subscribes_bt, admin_get_users_bt)
admin_kb.row(admin_send_all_bt, admin_gateways_bt)
admin_kb.row(back_bt)


def account_kb(account, is_subscribed=False, pag_data=None):
    kb = InlineKeyboardMarkup()
    if pag_data:
        left_bt, right_bt = None, None
        if pag_data.get('left'):
            call_left_data = f"{pag_data['command']} {account} left:{pag_data['left']}"
            left_bt = InlineKeyboardButton(text=ButtonText.left,
                                           callback_data=call_left_data)
        if pag_data.get('right'):
            call_right_data = f"{pag_data['command']} {account} right:{pag_data['right']}"
            right_bt = InlineKeyboardButton(text=ButtonText.right,
                                            callback_data=call_right_data)
        pag_buttons = [i for i in (left_bt, right_bt) if i]
        kb.row(*pag_buttons) if pag_buttons else None

    info_bt = InlineKeyboardButton(text=ButtonText.info,
                                   callback_data=f"{CallBackCommands.info} {account}")
    balances_bt = InlineKeyboardButton(text=ButtonText.balances,
                                       callback_data=f"{CallBackCommands.balances} {account}")
    openorders_bt = InlineKeyboardButton(text=ButtonText.openorders,
                                         callback_data=f"{CallBackCommands.openorders} {account}")
    history_bt = InlineKeyboardButton(text=ButtonText.history,
                                      callback_data=f"{CallBackCommands.history} {account}")

    kb.row(info_bt, balances_bt)
    kb.row(openorders_bt, history_bt)

    if dp.notifier:
        if is_subscribed:
            subscribe_bt = InlineKeyboardButton(text=ButtonText.unsubscribe_from,
                                                callback_data=f"{CallBackCommands.unsubscribe} {account}")
            to_subs_bt = InlineKeyboardButton(text=ButtonText.to_subs,
                                              callback_data=f"{CallBackCommands.to_subs} {account}")
            kb.row(subscribe_bt, to_subs_bt)
        else:
            subscribe_bt = InlineKeyboardButton(text=ButtonText.subscribe_to,
                                                callback_data=f"{CallBackCommands.subscribe} {account}")
            kb.row(subscribe_bt)

    return kb


def market_kb(market, is_subscribed=False, pag_data=None):
    kb = InlineKeyboardMarkup()
    if pag_data:
        left_bt, right_bt = None, None
        if pag_data.get('left'):
            call_left_data = f"{pag_data['command']} {market} left:{pag_data['left']}"
            left_bt = InlineKeyboardButton(text=ButtonText.left,
                                           callback_data=call_left_data)
        if pag_data.get('right'):
            call_right_data = f"{pag_data['command']} {market} right:{pag_data['right']}"
            right_bt = InlineKeyboardButton(text=ButtonText.right,
                                            callback_data=call_right_data)

        pag_buttons = [i for i in (left_bt, right_bt) if i]
        kb.row(*pag_buttons) if pag_buttons else None

    ticker_bt = InlineKeyboardButton(text=ButtonText.ticker, callback_data=f"{CallBackCommands.ticker} {market}")
    reverse_market_bt = InlineKeyboardButton(text=ButtonText.reverse_market,
                                             callback_data=f"{CallBackCommands.ticker} "
                                                           f"{market.split('/')[1]}/{market.split('/')[0]}")
    asks_bt = InlineKeyboardButton(text=ButtonText.asks, callback_data=f"{CallBackCommands.asks} {market} ")
    bids_bt = InlineKeyboardButton(text=ButtonText.bids, callback_data=f"{CallBackCommands.bids} {market} ")
    trades_bt = InlineKeyboardButton(text=ButtonText.trades, callback_data=f"{CallBackCommands.trades} {market}")

    kb.row(ticker_bt, reverse_market_bt)
    kb.row(bids_bt, trades_bt, asks_bt)
    if dp.notifier:
        if is_subscribed:
            subscribe_bt = InlineKeyboardButton(text=ButtonText.unsubscribe_from,
                                                callback_data=f"{CallBackCommands.unsubscribe} {market}")
            to_subs_bt = InlineKeyboardButton(text=ButtonText.to_subs,
                                              callback_data=f"{CallBackCommands.to_subs} {market}")
            kb.row(subscribe_bt, to_subs_bt)
        else:
            subscribe_bt = InlineKeyboardButton(text=ButtonText.subscribe_to,
                                                callback_data=f"{CallBackCommands.subscribe} {market}")
            kb.row(subscribe_bt)

    return kb


async def my_subscriptions_kb(subscriptions):
    kb = InlineKeyboardMarkup()

    for s in subscriptions:
        account = await get_account(s)
        if s[2] == '2':
            text = f"👤{account.name}"
        elif '/' in s:
            text = f"📊{s}"
        else:
            text = s
        kb.row(InlineKeyboardButton(text=text, callback_data=f"{CallBackCommands.explore} {s}"))
    return kb


def gateways_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for g in gateways_info.keys():
        bt_text = f"{g}"
        bt = KeyboardButton(text=bt_text)
        kb.row(bt)
    kb.row(back_bt)
    return kb


def gateway_kb(gateway):
    kb = InlineKeyboardMarkup()
    trade_bt = InlineKeyboardButton(text=ButtonText.trade_on_gw.format(gateway['name']), url=gateway['url'])
    kb.row(trade_bt)
    return kb


async def notification_kb(account=None, market=None, invertible=False):
    kb = InlineKeyboardMarkup()

    if account:
        account = (await get_account(account)).name
        kb.row(InlineKeyboardButton(text=f"👤{account}",
                                    callback_data=f"{CallBackCommands.explore} {account}"))
    if market:
        kb.row(InlineKeyboardButton(text=f"📊{market}",
                                    callback_data=f"{CallBackCommands.explore} {market}"))
    if invertible:
        kb.row(InlineKeyboardButton(text=ButtonText.invert,
                                    callback_data=f"{CallBackCommands.invert} {market}"))
    return kb


def build_wallet_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    for name in wallet_data.keys():
        kb.row(KeyboardButton(text=name))
    kb.row(back_bt)
    return kb


def operations_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in ButtonText.operations.values():
        kb.row(KeyboardButton(text=i))
    kb.row(back_bt)
    return kb


def operation_build_kb(op_type):
    kb = InlineKeyboardMarkup(row_width=3)

    kb.add(InlineKeyboardButton(text=ButtonText.broadcast, callback_data=f"{CallBackCommands.broadcast} {op_type}"))
    kb.add(InlineKeyboardButton(text=ButtonText.destroy_op, callback_data=CallBackCommands.destroy))
    return kb


if cfg['plugins']['wallet']:
    wallet_kb = build_wallet_kb()
else:
    wallet_kb = back_kb

to_git_kb = InlineKeyboardMarkup()

to_git_kb.row(InlineKeyboardButton(text=ButtonText.to_source, url=SOURCE_CODE_URL))


keyboards = {
    "start": start_kb,
    wallet_bt.text: wallet_kb,
    explorer_bt.text: explorer_kb,
    notifier_bt.text: notifier_kb,

    explore_accounts_bt.text: back_kb,
    explore_markets_bt.text: back_kb,
    explore_fee_schedule_bt.text: back_kb,

    notifier_my_subscriptions_bt.text: back_kb,
}
