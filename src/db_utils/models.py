import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from config import SQL_CONN_URL, FREE_SUBS_LIMIT


# not-async engine for using in migrations
engine = create_engine(SQL_CONN_URL, echo=False)
Base = declarative_base()


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id = Column(Integer, primary_key=True, unique=True)
    is_bot = Column(Boolean)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)

    added = Column(DateTime, default=datetime.datetime.now())

    subscriptions_limit = Column(Integer, default=FREE_SUBS_LIMIT)


class Subsription(Base):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, unique=True)
    bts_object = Column(String)

    telegram_user_id = Column(Integer, ForeignKey(TelegramUser.id))
    telegram_user = relationship('TelegramUser', remote_side=TelegramUser.id)

    last_op = Column(Integer)
    last_price = Column(DECIMAL)

    price_change_percent = Column(Numeric)

    muted = Column(Boolean, default=False)


def create_all():
    Base.metadata.create_all(engine)
