from aiogram.utils.markdown import hcode, hbold, hitalic

from config import PROJECT_NAME, SOURCE_CODE_URL, CREATOR_USERNAME


class ButtonText:
    push_me = "push_me"

    back = "↖️Back"

    wallet = "🧰Wallet"
    explorer = "🔍Explorer"
    notifier = "📣Notifier"
    gateways = "🏦Gateways"
    donate = "Donate🙏"
    start_buttons_text = (wallet, explorer, notifier, gateways, donate)

    accounts = "👤Accounts"
    markets = "📊Markets"
    fee_schedule = "🧾Fee Schedule"
    explorer_buttons_text = (accounts, markets, fee_schedule)

    my_subscriptions = "My subscriptions"
    notifier_buttons_text = (my_subscriptions, )

    info = "ℹ️Info"
    openorders = "📖Open Orders"
    balances = "💳Balances"
    history = "📜History"

    ticker = "📰Ticker"
    reverse_market = "🔁Reverse"
    asks = "↙️Asks"
    bids = "Bids↗️"
    trades = "🤝Trades"

    subscription_settings = "⚙️Settings"
    add = '➕'
    sub = '➖'
    ok = "🆗"
    cancel = "🔙"

    subscribe_to = "🔔Subscribe"
    unsubscribe_from = "🔕Unsubscribe"
    to_subs = "↩My subscriptions list"

    invert = "🔃Invert"

    trade_on_gw = "Trade on {}"

    admin_get_users = "Get users"
    admin_get_subscriptions = "Get subscribes"
    admin_send_all = "Send all"
    admin_gateways = "Gateways"

    left = "⬅️"
    right = "➡️"

    send = "🔵Send"
    exchange = "💱Place order"
    cancel_order = "🔴Cancel order"

    broadcast = "🖊Broadcast"
    destroy_op = "❌Cancel"

    operations = {
        0: send,
        1: exchange,
        2: cancel_order
    }

    permissions = "🔑Permissions"

    to_source = "Source code"


class TextMessage:
    start = f"Welcome to {PROJECT_NAME}!\n\n" \
            f"{hbold('Main menu')}\n" \
            f"Use /restart to back here if bot have some unexpected behavior.\n" \
            f"All bugs, requests, text mistakes etc. you can send to {CREATOR_USERNAME}"

    wallet = f"{hbold('Wallet menu')}\n" + "Current active account is {}" + "\n\nYou can choose any other account\n" \
             f"If there is no accounts, " \
             f"add them in {hcode('config/wallet.yaml')} file\n\n" \
             f"Available commands:\n\n/transfer\n/sell\n/buy\n/cancel\n\n🎓Tap command without arguments to learn more"
    default_account_change = "✅Active account switched to {}"
    wallet_not_in_root = f"🛑Run your own {PROJECT_NAME} instance to use the " \
                         f"{hbold('Wallet')} plugin\n\n {SOURCE_CODE_URL}!"
    explorer = f"{hbold('Explorer menu')}\n"
    notifier = f"{hbold('Notifier menu')}\n"
    gateways = f"{hbold('Gateways menu')}"

    donate = f"If you want support TeleShares development, you can send me any cryptocurrency:\n\n"

    plugin_disabled = "Plugin {} is currently disabled"

    explore_accounts = "Enter account name or ID"
    explore_markets = f"Enter market (two Bitshares asset names or IDs separated buy space or / symbol, like\n" \
                      f"{hcode('bts/usd')}\n" \
                      f"or\n" \
                      f"{hcode('RUDEX.BTC GDEX.BTC')}\n" \
                      f"or\n" \
                      f"{hcode('1.3.0/1.3.113')}\n" \
                      f"Please, enter bitASSETs without {hcode('bit')} prefix. " \
                      f"So to explore bitCNY/USD, enter just CNY/USD"

    explore_fee_schedule = f"{hbold('Current blockchain fees')}\n\n"

    explorer_answers = {ButtonText.accounts: explore_accounts,
                        ButtonText.markets: explore_markets,
                        ButtonText.fee_schedule: explore_fee_schedule,
                        }

    notifier_my_subscriptions = "Choose bithsares object you want to browse from your subscriptions:\n"
    notifier_get_premium = "There will be instruction to buy premium account"
    notifier_answers = {
        'no_subscriptions': "Currently you don't subscribed to any bitshares object",
        ButtonText.my_subscriptions: notifier_my_subscriptions,
    }

    successfully_subscribed_account = "You have successfully subscribed to account {}. " \
                                      "You will receive notifications about new operations"
    successfully_subscribed_market = "You have successfully subscribed to market {}. " \
                                     "You will receive notifications when the price changes by 5%"
    successfully_unsubscribed = "You have unsubscribed from {}"

    market_subscribe_settings = f"Enter value of % market price changing you want to receive notifications\n" \
                                f"{hitalic('Enter 0 if you want to know about ANY price changing on market')}"

    request_processing = "Request processing... Please, wait..."
    no_enought_limit = "You have reached the limit of free subscriptions. If you want to subscribe this object, " \
                       "you need to buy premium or unsubscribe from objects you are subscribed now"
    reached_system_subs_limit = "Unfortunately this application instance has reached limit of subscriptions" \
                                "If you are owner, you can fix MAX_SUBSCRIPTIONS constant in config"

    no_account = "There is no account {} in BitShares blockchain. Try again"
    bad_market = "Bad market! Try again"
    unknown_error = "Unknown error. Try again"
    no_account_openorders = "{} has no open orders"
    no_orders_on_market = "There is no {} on this market"
    no_trades_on_market = "There is no last trades on this market"
    no_gateways = "There is no gateway {} or TeleShares don't know about it. " + f"" \
                                                                                 f"If you want to add your gateway " \
                                                                                 f"here, write me {CREATOR_USERNAME}"
    no_btc_ticker = "No ticker"

    experimental_feature = "It's an experimental feature. Small screen may have some problems with table view"

    operations_build = {'transfer': "Sending the transfer",
                        'sell': "Placing the limit order",
                        'buy': "Placing the limit order",
                        'cancel': "Canceling the limit order",
                        }
    enter_param_for_op = "Enter the {} value"

    broadcast = "👍Operation successfully was broadcast! TransactionID is {}"
    failed_to_broadcast = "Operation failed to broadcast with error: {}"

    transfer_wallet_hint = f"Transfer:\n{hitalic('/transfer Amount Asset To [Memo(optional)]')}\n" \
                           f"Example:\n" \
                           f"{hcode('/transfer 5 BTS teleshares2020 [Thank you for your bot!]')}\n\n"
    cancel_wallet_hint = f"Cancel order:\n{hcode('/cancel 1.7.8888 1.7.9999')}\nor\n{hcode('/cancel 8888 9999')}\n\n"
    exchange_wallet_hint = f"Exchange:\n" \
                           f"{hbold('⚠️WARNING! IT IS VERY EXPERIMENTAL FUNCTION! USE IT IF YOU ARE SURE YOU KNOW HOW IT WORKS')}\n\n" \
                           f"Amount by PRICE\n{hitalic('/action AmountToSell AssetToSell price PRICE AssetToBuy/AssetToSell')}\n" \
                           f"or\n" \
                           f"{hitalic('/action AmountToSell AssetToSell price PRICE AssetToBuy')}\n" \
                           f"or\n" \
                           f"Amount for Amount\n{hitalic('/action AmountToSell AssetToSell for AmountToBuy AssetToBuy')}\n\n" \
                           f"Example:\n" \
                           f"{hcode('/sell 1000 USD price 6.5 USD/CNY')}\n" \
                           f"or\n" \
                           f"{hcode('/sell 1000 USD price 6.5 CNY')}\n" \
                           f"or\n" \
                           f"{hcode('/buy 0.1 rudex.btc for 50000 BTS now')}\n"

    operations_hints = {
        'transfer': transfer_wallet_hint,
        'cancel': cancel_wallet_hint,
        "buy": exchange_wallet_hint,
        "sell": exchange_wallet_hint
    }
    bad_operation = "❗️Error when parse operation arguments\n\n" \
                    "Send command /{} without arguments to see hint for this operation"


class AdminTextMessage:
    root_greeting = f"{PROJECT_NAME} started!"
    reconnected = "Successfully connected to " + hcode("{}")


class BtsObjectRepr:
    account = "{}\n" + \
              "{}\n" + \
              "{}\n" + \
              "###\n"

    ltm = "⚡️"
    balance = "{}\n"
    openorder = "{}\n" \
                "Buy {}\n"

    ticker = f"{hcode('latest:    ')} " + "{}\n" + \
             f"{hcode('change:    ')} " + "{}\n\n" \
                                          f"{hcode('volume24:  ')} " + "{}\n\n"

    operations = {
        0: "🔵{} sent {} to {}\n",
        1: "🟠{} placed an order {} to \nsell: {}\nbuy: {}\nprice: {}\n",
        2: "🔴{} cancelled order {}\n",
        4: "🟢{} fill_order {}\nbought: {}\nsold: {}\nprice: {}\n",
        5: "🟤{} registered the account {}\n",
        14: "⚪️{} issued {} to {}\n",
    }

    price_change = "{}\n" \
                   "price: {}\n" \
                   "{} %"

    order_in_book = "{}|{}|{}\n"
    number_of_orders_shown = "Top {} of {} orders shown\n"
    fee_schedule = ""

    gateway_view = "{}\n" \
                   f"{hcode('URL:      ')}" + "{}\n" \
                   f"{hcode('Telegram: ')}" + "{}\n" \
                   f"{hcode('Status:   ')}" + "{}\n" \
                   f"{hcode('Country:  ')}" + "{}\n" \
                   f"{hcode('KYC:      ')}" + "{}\n" \
                   f"{hcode('Age:      ')}" + "{} days\n\n" \
                   f"{hcode('Updated:   ')}" + "{}\n\n" \
                   f"" \
                   f"{hcode('BTC/BTS volume24:')}\n" + "{}\n"

    account_balances_table_header = ("Asset", "Amount")


class SystemLogs:
    start_history_parser = 'Starting history notifier loop'
    process_new_history_check_iter = "Processing new history check iteration"
    retrieved_new_operations = "Retrieved {} new operations"
    received_message_log = "received {} {} from {} in state {}"


class CallBackCommands:
    explore = 'explore'

    info = 'info'
    openorders = 'open_orders'
    balances = 'balances'
    history = 'history'

    subscribe = 'subscribe'
    unsubscribe = 'unsubscribe'
    to_subs = 'to_subs'

    ticker = 'ticker'
    reverse_market = 'reverse'
    asks = 'asks'
    bids = 'bids'
    trades = 'trades'

    permissions = "permissions"

    subscription_settings = 'settings'
    ok = 'ok'
    cancel = 'cancel'

    invert = 'invert'
    right = 'right'
    left = 'left'
    pag_commands = (left, right)
    frames_commands = (
        info, balances, openorders, history, ticker, reverse_market, asks, bids, trades
    )

    send = "send"
    exchange = "exchange"

    operations = {
        0: send,
        1: exchange
    }

    broadcast = "broadcast"
    destroy = "destroy"
    set_param = "set"


gateways_emoji = {
    "unknown": '❓',
    "active": {True: "✅Yes",
               False: "❌No"},
    "kyc": {True: "❗️Yes",
            False: "✅No"},
    "country": {"Russia": "🇷🇺Russia",
                "China": "🇨🇳China"}
}
