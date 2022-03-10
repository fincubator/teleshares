import random
import re
from decimal import Decimal

from aiogram.utils.markdown import hcode

from bitshares.aio import BitShares
from bitshares.aio.instance import set_shared_bitshares_instance, shared_bitshares_instance
from bitshares.aio.account import Account
from bitshares.aio.asset import Asset
from bitshares.aio.amount import Amount
from bitshares.aio.market import Market
from bitshares.aio.dex import Dex
from bitshares.aio.price import Price, Order
from bitshares.aio.market import Market

from bitsharesbase.account import default_prefix
from bitsharesbase.signedtransactions import Signed_Transaction
from graphenecommon.exceptions import AccountDoesNotExistsException, AssetDoesNotExistsException
from grapheneapi.exceptions import NumRetriesReached

from src.text_content import ButtonText

from config import nodes, wallet_data


def nodes_smart_choose():
    # TODO need to choose best node
    return random.choice(nodes)


async def init_bitshares(loop=None, node=None) -> BitShares:
    """ Create bitshares aio.instance, append it to loop and set as shared """
    if not node:
        node = nodes_smart_choose()
    kwargs = dict(loop=loop, node=node, nobroadcast=bool(not wallet_data))

    if wallet_data:
        keys = []
        for account, account_keys in wallet_data.items():
            for k in account_keys.values():
                keys.append(k)
        kwargs["keys"] = keys

    bitshares_instance = BitShares(**kwargs)
    set_shared_bitshares_instance(bitshares_instance)
    await bitshares_instance.connect()
    return bitshares_instance


async def reconnect(node=None):
    """ Manually change the bitshares node """
    # TODO not working! Bug in pybitshares.aio
    instance: BitShares = shared_bitshares_instance()
    try:
        if not node:
            node = nodes_smart_choose()
            await instance.rpc.connection.disconnect()
            instance.rpc.url = node
        await instance.connect()
        return node
    except NumRetriesReached:
        await reconnect()


def set_default_account(account):
    instance: BitShares = shared_bitshares_instance()
    instance.set_default_account(account)


def get_default_account():
    instance: BitShares = shared_bitshares_instance()
    return instance.config['default_account']


def _to_account(string):
    if isinstance(string, str):

        string = string.lower()
        # if received string 1.2.x
        if "1.2." in string:
            return string

        # if received integer id (x in 1.2.x object)
        try:
            int(string)
            return f"1.2.{string}"
        except ValueError:
            pass

        # if received account name
        return string
    elif isinstance(string, Account):
        return string['id']
    else:
        return


def _to_market(string):
    string = string.upper()
    if len(string.split()) == 2:
        return f"{string.split()[0]}/{string.split()[1]}"
    return string


async def get_account(account):
    try:
        account = _to_account(account)
        account = await Account(account)
        return account
    except AccountDoesNotExistsException:
        return None


async def get_new_ops(account, old_op=0, **kwargs):
    account = await get_account(account)
    history_agen = account.history(last=old_op)
    ops = [op async for op in history_agen]
    return ops


async def get_last_op(account) -> int:
    history = await get_new_ops(account, limit=1)
    return int(history[0]['id'].split('.')[2])


async def get_market(market) -> Market or None:
    try:
        market = _to_market(market)
        market = await Market(market)
        return market
    except AssetDoesNotExistsException:
        return None
    except Exception as ex:
        return None


async def get_ticker(market):
    market = await get_market(market)
    return await market.ticker()


async def get_new_price(market) -> float:
    ticker = await get_ticker(market)
    return ticker['latest']['price']


async def get_fee_schedule() -> dict:
    fees = await Dex().returnFees()
    return fees


async def broadcast(**kwargs):
    try:
        instance: BitShares = shared_bitshares_instance()
        op_type = kwargs.pop("op_type")
        if op_type == 'transfer':
            tx = await instance.transfer(**kwargs)
            return Signed_Transaction(tx).id

        if op_type in ('sell', "buy"):
            market_name = kwargs.pop("market")
            market: Market = await Market(str(market_name))
            if op_type == 'sell':
                func = market.sell
            else:
                func = market.buy
            # TODO try Decimal for amount
            amount = await Amount(kwargs["amount"])
            kwargs["amount"] = amount

            order = await func(returnOrderId=True, **kwargs)
            import pprint
            return f"{Signed_Transaction(order).id}\n\nOrderID is {hcode(order['orderid'])}"

        if op_type == 'cancel':
            tx = await instance.cancel(**kwargs)
            return Signed_Transaction(tx).id
    except Exception as ex:
        return ex


async def parse_operation(op_text, command):
    try:
        op_split = op_text.split()
        op_body = dict()

        if command == 'transfer':

            amount = op_split[0]
            asset = op_split[1].upper()
            to = op_split[2].lower()
            memo = re.search(r"[^[]*\[([^]]*)\]", op_text)
            if memo:
                memo = memo.group(1)
            else:
                memo = ''

            op_body = {
                "amount": amount,
                "asset": asset,
                "to": to,
                "memo": memo,
                "op_type": command
            }

        if command in ('sell', "buy"):
            killfill = False

            amount = f"{op_split[0]} {op_split[1].upper()}"

            if op_split[2] == "price":
                if '/' in (op_split[4]):
                    price = f"{op_split[3]}"
                    market = op_split[4].upper()
                else:
                    price = f"{op_split[3]}"
                    market = f"{op_split[4]}/{op_split[1]}".upper()

            elif op_split[2] == "for":
                _base_amount = await Amount(f"{op_split[3]} {op_split[4].upper()}")
                market = f"{(await _base_amount.asset).symbol}/{op_split[1]}".upper()
                price = f"{_base_amount.amount / Decimal(op_split[0])} {market}"

            else:
                raise

            op_body = {
                'amount': amount,
                'price': price,
                'market': market,
                "op_type": command,
                "killfill": "now" in op_split[-1] in ("now", "killfill")
            }

        if command == 'cancel':
            orders = []
            for order in op_split:
                if "1.7." in order:
                    orders.append(order)
                else:
                    orders.append(f"1.7.{order}")

            op_body = {"orderNumbers": orders,
                       "op_type": "cancel"}

        return op_body
    except Exception as ex:
        return ex
