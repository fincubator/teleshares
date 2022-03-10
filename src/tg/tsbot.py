import asyncio

from aiogram import Bot
from aiogram.types import ParseMode
from aiogram.utils.exceptions import *

from src.text_content import AdminTextMessage
from src.bitshares_utils.base import init_bitshares
from src.db_utils.queries import init_database

from config import TG_SLEEP_TIME

DEFAULT_PARSE_MODE = ParseMode.HTML


class TeleSharesBot(Bot):
    """
    Class ``TeleSharesBot``
    """

    def __init__(self, root_id, *args, **kwargs):
        self.root_id = root_id

        self.bitshares = None
        self.db = None

        super().__init__(*args, **kwargs)
        if not kwargs.get('parse_mode'):
            self.parse_mode = DEFAULT_PARSE_MODE
            self.loop.run_until_complete(self.set_bitshares())
            self.loop.run_until_complete(self.set_database())

    async def root_greeting(self):
        await self.send_message(chat_id=self.root_id, text=AdminTextMessage.root_greeting)

    async def set_bitshares(self):
        self.bitshares = await init_bitshares(loop=self.loop)

    async def set_database(self):
        if not self.db:
            self.db = await init_database()
            return

    async def safe_send_message(self, text=None, chat_id=None, reply_markup=None, **kwargs):
        try:
            msg = await self.send_message(text=text, chat_id=chat_id, reply_markup=reply_markup, **kwargs)

            # To prevent Telegram ban
            await asyncio.sleep(TG_SLEEP_TIME)
            return msg
        except BotBlocked:
            pass
        except UserDeactivated:
            pass
        except ChatNotFound:
            pass

    async def safe_delete_message(self, message_id, chat_id=None):
        if not chat_id:
            chat_id = self.root_id
        try:
            await self.delete_message(chat_id=chat_id,
                                      message_id=message_id)
        except MessageToDeleteNotFound:
            pass
        except MessageCantBeDeleted:
            pass
        except BotBlocked:
            pass
        except UserDeactivated:
            pass
        except ChatNotFound:
            pass

    async def safe_edit_message(self, message_id, text=None, chat_id=None, reply_markup=None):
        if not chat_id:
            chat_id = self.root_id
        try:
            if text:
                await self.edit_message_text(message_id=message_id,
                                             chat_id=chat_id,
                                             text=text,
                                             reply_markup=reply_markup)
            else:
                await self.edit_message_reply_markup(message_id=message_id,
                                                     chat_id=chat_id,
                                                     reply_markup=reply_markup)

        except MessageCantBeEdited:
            pass
        except MessageNotModified:
            pass
        except MessageToEditNotFound:
            pass
        except BotBlocked:
            pass
        except UserDeactivated:
            pass
        except ChatNotFound:
            pass
