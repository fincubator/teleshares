from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup


class StartState(StatesGroup):
    start = State()
    wallet = State()
    explorer = State()
    notifier = State()
    gateways = State()


class ExplorerState(StatesGroup):
    accounts = State()
    markets = State()
    fee_schedule = State()


class NotifierState(StatesGroup):
    my_subscriptions = State()


class WalletState(StatesGroup):
    operation_build = State()


class GatewaysState(StatesGroup):
    main = State()


states_groups = (GatewaysState, WalletState, NotifierState, ExplorerState, StartState)
