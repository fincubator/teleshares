import pytest
from src.bitshares_utils.base import *

from tests.fixtures import *


@pytest.mark.asyncio
async def test_account():
    await init_bitshares()
    account = await get_account(test_bts_account)
    assert isinstance(account, Account)


@pytest.mark.asyncio
async def test_market():
    await init_bitshares()
    market = await get_market(test_bts_market)
    assert isinstance(market, Market)


@pytest.mark.asyncio
async def test_get_new_price():
    await init_bitshares()
    price = await get_new_price(test_bts_market)
    assert isinstance(price, float)


@pytest.mark.asyncio
async def test_fee_schedule():
    await init_bitshares()
    fee = await get_fee_schedule()
    assert isinstance(fee, dict)


@pytest.mark.asyncio
async def test_get_new_ops():
    await init_bitshares()
    ops = await get_new_ops(test_bts_account)
    assert isinstance(ops, list)
    pre_last_op = ops[1]['id'].split('.')[2]
    cuted_ops = await get_new_ops(test_bts_account, old_op=pre_last_op)
    assert len(cuted_ops) == 1


@pytest.mark.asyncio
async def test_get_last_op():
    await init_bitshares()
    last_op = await get_last_op(test_bts_account)
    assert isinstance(last_op, int)


@pytest.mark.asyncio
async def test_default_account():
    set_default_account(test_bts_account)
    assert get_default_account() == test_bts_account