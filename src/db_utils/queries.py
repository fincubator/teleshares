import aiopg.sa
from sqlalchemy.sql import insert, select, delete, update
from src.db_utils.models import TelegramUser, Subsription

from config import pg_config


async def init_database():
    # Async engine to execute clients requests
    engine = await aiopg.sa.create_engine(**pg_config)
    return engine


async def add_telegram_user(conn, **user_data):
    try:
        await conn.execute(insert(TelegramUser).values(**user_data))
    except:
        pass


async def get_all_users(conn):
    cursor = await conn.execute(select([TelegramUser]).as_scalar())
    users = await cursor.fetchall()
    return users


async def get_all_subscriptions(conn):
    cursor = await conn.execute(select([Subsription]).as_scalar())
    subs = await cursor.fetchall()
    return subs


async def get_user_by_id(conn, user_id):
    cursor = await conn.execute(select([TelegramUser]).where(TelegramUser.id == user_id).as_scalar())
    user = await cursor.fetchone()
    return user


async def is_subscribed_to(conn, telegram_user_id, bts_object):
    is_subs = False
    bts_objects = []
    if bts_object[2] == '2':
        bts_objects = [bts_object]
    if '/' in bts_object:
        bts_objects = [bts_object, f"{bts_object.split('/')[1]}/{bts_object.split('/')[0]}"]

    for obj in bts_objects:

        cursor = await conn.execute(select([Subsription])
                                    .where(Subsription.bts_object == obj
                                           and
                                           Subsription.telegram_user_id == telegram_user_id)
                                    .as_scalar())
        user = await cursor.fetchone()
        if bool(user):
            is_subs = True
            break
    return is_subs


async def subscribe_to(conn, **kwargs):
    is_sub = await is_subscribed_to(conn, kwargs["telegram_user_id"], kwargs["bts_object"])
    if not is_sub:
        try:
            await conn.execute(insert(Subsription).values(**kwargs))
            is_sub = True
        except:
            pass
    return is_sub


async def unsubscribe_from(conn, telegram_user_id, bts_object):
    await conn.execute(delete(Subsription).where(Subsription.bts_object == bts_object
                                                 and
                                                 Subsription.telegram_user_id == telegram_user_id))


async def get_user_subscriptions(conn, telegram_user_id):
    cursor = await conn.execute(
        select([Subsription]).where(Subsription.telegram_user_id == telegram_user_id).as_scalar())
    subs = await cursor.fetchall()
    if subs:
        return [i.bts_object for i in subs]


async def allow_to_add_new_subscription(conn, telegram_user_id):
    subs = await get_user_subscriptions(conn, telegram_user_id)
    user = await get_user_by_id(conn, telegram_user_id)
    if not subs:
        len_subs = 0
    else:
        len_subs = len(subs)
    return user.subscriptions_limit > len_subs


async def set_new_op(conn, subscription_id, new_op):
    await conn.execute(update(Subsription)
                       .values(
        {Subsription.last_op: new_op})
                       .where(Subsription.id == subscription_id))


async def set_new_price(conn, subscription_id, new_price):
    await conn.execute(update(Subsription)
                       .values(
        {Subsription.last_price: new_price})
                       .where(Subsription.id == subscription_id))
