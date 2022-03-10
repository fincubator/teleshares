import datetime
import textwrap

from bitsharesbase.operations import getOperationNameForId
from aiogram.utils.markdown import hbold, hcode
from terminaltables import AsciiTable

from src.text_content import BtsObjectRepr, TextMessage, gateways_emoji, ButtonText, CallBackCommands
from src.bitshares_utils.base import *


async def account_view(account_name, title=None, frame_data=None, frame=None):
    kwargs = {}
    if not frame:
        frame = CallBackCommands.info

    if not title:
        title = frame.lower()

    frame = ACCOUNT_VIEWS[frame]

    if frame == account_history_frame:
        kwargs['subject_account'] = account_name
    frame_result = await frame(frame_data, **kwargs)
    return f"👤{hbold(account_name)}\n{title}\n\n{frame_result}"


async def account_info_frame(frame_data, **kwargs):
    table = AsciiTable(table_data=frame_data)
    table.outer_border = False
    table.inner_row_border = True
    return hcode(table.table)


async def account_balances_frame(frame_data, **kwargs):
    table_data = [BtsObjectRepr.account_balances_table_header]
    for b in frame_data:
        table_data.append(
                [
                    textwrap.fill(b.symbol, 10).replace('.', '.\n'), "%f" % b.amount
                ]
            )

    table = AsciiTable(table_data=table_data)
    table.outer_border = False
    table.inner_row_border = True

    return hcode(table.table)


async def account_openorders_frame(frame_data, **kwargs):
    if isinstance(frame_data, str):
        table_data = [[frame_data]]
    else:
        table_data = []
        for o in frame_data:
            table_data.append(
                [textwrap.fill(format_account_openorder(o) + '\n\n', 60)]
            )
    table = AsciiTable(table_data=table_data)
    table.outer_border = False
    table.inner_row_border = False
    table.inner_heading_row_border = False
    table.CHAR_INNER_HORIZONTAL = " "
    return table.table


async def account_history_frame(frame_data, **kwargs):
    subject_account = kwargs['subject_account']
    table_data = []
    for op in frame_data:
        table_data.append(
                [
                    await format_op(op, account=subject_account)
                ]
            )
    table = AsciiTable(table_data=table_data)
    table.outer_border = False
    table.inner_heading_row_border = False
    table.inner_row_border = False
    return table.table


async def market_view(market_name, title=None, frame_data=None, frame=None) -> str:
    kwargs = {}

    if not frame:
        frame = CallBackCommands.ticker

    if title == ButtonText.reverse_market:
        title = CallBackCommands.ticker

    if not title:
        title = frame.lower()

    frame = MARKET_VIEWS[frame]
    frame_result = await frame(frame_data, **kwargs)
    return f"📊{hbold(market_name)}\n{title}\n\n{frame_result}"


async def market_ticker_frame(frame_data, **kwargs):
    percent_change = frame_data['percentChange']
    if percent_change > 0:
        percent_change = f"📈{percent_change} %"
    elif percent_change < 0:
        percent_change = f"📉{percent_change} %"
    else:
        percent_change = f"{percent_change} %"
    latest: str = str(frame_data['latest']).split('/')[0]
    volume24 = frame_data['baseVolume']
    return BtsObjectRepr.ticker.format(latest, percent_change,
                                       volume24)


async def market_trades_frame(frame_data, **kwargs):
    data = []
    if isinstance(frame_data, str):
        data.append([frame_data])
    else:
        for t in frame_data:
            data.append(
                [
                    format_market_trade(t)
                ]
            )
    table = AsciiTable(table_data=data)
    table.outer_border = False
    table.inner_heading_row_border = False
    table.inner_row_border = False
    return table.table


async def market_orderbook_frame(frame_data, **kwargs):
    if isinstance(frame_data, str):
        table_data = [[frame_data]]
    else:
        table_data = []
        for i in frame_data:
            try:
                table_data.append(
                    ["%f" % i["quote"].amount, "%f" % i["price"]]
                )
            except:
                table_data.append([i, "Price"])

    table = AsciiTable(table_data=table_data)
    table.outer_border = False
    table.inner_row_border = False
    return hcode(table.table)


def format_account_openorder(order):
    return BtsObjectRepr.openorder.format(hcode(order['id']), order)


async def format_op(op, account):
    op_type = op['op'][0]
    _template = BtsObjectRepr.operations.get(op_type)
    if op_type == 0:
        _from = await Account(op['op'][1]['from'])
        _amount = await Amount(op['op'][1]['amount'])
        _to = await Account(op['op'][1]['to'])
        pretty_op = _template.format(
            _from.name, _amount, _to.name
        )
    elif op_type == 1:
        _seller = await Account(op['op'][1]['seller'])
        _order_id = hcode(op['result'][1])
        _amount_to_sell = await Amount(op['op'][1]['amount_to_sell'])
        _min_to_receive = await Amount(op['op'][1]['min_to_receive'])
        _price = await (_amount_to_sell / _min_to_receive) # TODO RuntimeWarning: coroutine 'Amount.copy' was never awaited
        pretty_op = _template.format(
            _seller.name,
            _order_id,
            _amount_to_sell,
            _min_to_receive,
            _price
        )
    elif op_type == 2:
        _fee_paying_account = await Account(op['op'][1]['fee_paying_account'])
        _order_id = op['op'][1]['order']

        pretty_op = _template.format(
            _fee_paying_account.name,
            _order_id,
        )
    elif op_type == 4:
        _account = await Account(op['op'][1]['account_id'])
        _order_id = hcode(op['op'][1]['order_id'])
        _receives = await Amount(op['op'][1]['receives'])
        _pays = await Amount(op['op'][1]['pays'])
        _fill_price = await Price(op['op'][1]['fill_price'])

        pretty_op = _template.format(
            _account.name,
            _order_id,
            _receives,
            _pays,
            _fill_price
        )
    elif op_type == 5:
        _registrar =await Account(op['op'][1]['registrar'])
        _account = await Account(op['op'][1]['name'])

        pretty_op = _template.format(
            _registrar.name,
            _account.name
        )

    elif op_type == 14:
        _issuer = await Account(op['op'][1]['issuer'])
        _amount = await Amount(op['op'][1]['asset_to_issue'])
        _issue_to_account = await Account(op['op'][1]['issue_to_account'])
        pretty_op = _template.format(
            _issuer.name,
            _amount,
            _issue_to_account.name
        )
    else:
        pretty_op = f"{getOperationNameForId(op_type)}\n"
    _op_executor = await Account(account)
    _op_executor_name = _op_executor.name
    pretty_op = f"{hcode(op['id'])}\n{pretty_op}".replace(_op_executor_name, hbold(_op_executor_name))
    return pretty_op


def format_market_trade(trade):
    today = datetime.datetime.today()
    if today.date() == trade['time'].date():
        when = trade['time'].time()
    else:
        when = trade['time'].date()
    return f"{when}\n{trade['base']} for {trade['quote']}\n@{trade['price']}\n"


async def get_account_info_frame_data(account):
    if not isinstance(account, Account):
        account = await Account(account)
    bts_balance = await account.balance("BTS")
    if bts_balance > 0:
        _bts_balance = "%f" % bts_balance.amount
    else:
        _bts_balance = '0'

    registrar = await Account(account['registrar'])
    _frame_data = [
        ('id', account['id']),
        ('BTS', "%s" % _bts_balance),
        ('registrar', textwrap.fill(registrar.name, 14))]
    return _frame_data


async def fee_schedule_view(fees=None):
    # TODO Refactor this. Implement some pagination or separeta by op types. And add LTM mode
    fee_schedule = BtsObjectRepr.fee_schedule
    if not fees:
        fees = await get_fee_schedule()
    for op, op_details in fees.items():
        fee = '\n'
        if not op_details:
            fee += "    0 BTS\n"
        else:
            for k, v in op_details.items():
                fee += (f"    {k}: {v} BTS\n")

        fee_schedule += f"{hbold(op.upper())}{fee}\n"

    return fee_schedule


async def gateway_view(gateway_data):
    resp = str()
    for key, value in gateway_data.items():
        if key == "since":
            resp += f"{hcode(key)}: {(datetime.date.today() - gateway_data['since']).days} days\n"
        elif gateways_emoji.get(key):
            resp += f"{hcode(key)}: {gateways_emoji[key][value]}\n"
        else:
            resp += f"{hcode(key)}: {value}\n"
    resp += "\n"
    try:
        market = f"{gateway_data['name']}.BTC/BTS"
        _ticker = await get_ticker(market)
        btc_bts_vol24 = _ticker["quoteVolume"]
        resp += f"BTC/BTS 24h volume:\n{btc_bts_vol24}"
    except AssetDoesNotExistsException:
        resp += f"BTC/BTS 24h volume:\n{TextMessage.no_btc_ticker}"
    return resp


async def retrieve_market_name_from_op(op) -> str:
    if op['op'][0] == 4:
        market_name = f"{(await Asset(op['op'][1]['fill_price']['base']['asset_id'])).symbol}/" \
                      f"{(await Asset(op['op'][1]['fill_price']['quote']['asset_id'])).symbol}"
        return market_name
    if op['op'][0] == 1:
        market_name = f"{(await Asset(op['op'][1]['amount_to_sell']['asset_id'])).symbol}/" \
                      f"{(await Asset(op['op'][1]['min_to_receive']['asset_id'])).symbol}"
        return market_name


async def invert_price_in_message(msg):
    msg_array = msg.split('\n')
    for string in msg_array:
        if 'price:' in string:
            price_str = f"{string.split()[1]} {string.split()[2]}"
            price = await Price(price_str)
            new_msg = msg.replace(price_str, str(await price.invert()))
            return new_msg


async def permissions_frame(frame_data):
    frame = ""
    for key in ('active_key', 'memo_key', 'owner_key'):
        if frame_data.get(key):
            frame += f"{key.split('_')[0].capitalize()}: ✅\n"
        else:
            frame += f"{key.split('_')[0].capitalize()}: ❌\n"
    return frame


ACCOUNT_VIEWS = {
    CallBackCommands.info: account_info_frame,
    CallBackCommands.balances: account_balances_frame,
    CallBackCommands.openorders: account_openorders_frame,
    CallBackCommands.history: account_history_frame,
    CallBackCommands.permissions: permissions_frame
}

MARKET_VIEWS = {
    CallBackCommands.ticker: market_ticker_frame,
    CallBackCommands.trades: market_trades_frame,
    CallBackCommands.asks: market_orderbook_frame,
    CallBackCommands.bids: market_orderbook_frame
}
