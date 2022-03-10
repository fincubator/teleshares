from aiogram.types import KeyboardButton
from src.text_content import ButtonText

back_bt = KeyboardButton(text=ButtonText.back)

wallet_bt = KeyboardButton(text=ButtonText.wallet)
explorer_bt = KeyboardButton(text=ButtonText.explorer)
notifier_bt = KeyboardButton(text=ButtonText.notifier)
gateways_bt = KeyboardButton(text=ButtonText.gateways)
donate_bt = KeyboardButton(text=ButtonText.donate)

explore_accounts_bt = KeyboardButton(text=ButtonText.accounts)
explore_markets_bt = KeyboardButton(text=ButtonText.markets)
explore_fee_schedule_bt = KeyboardButton(text=ButtonText.fee_schedule)

notifier_my_subscriptions_bt = KeyboardButton(text=ButtonText.my_subscriptions)

admin_get_users_bt = KeyboardButton(text=ButtonText.admin_get_users)
admin_get_subscribes_bt = KeyboardButton(text=ButtonText.admin_get_subscriptions)
admin_send_all_bt = KeyboardButton(text=ButtonText.admin_send_all)
admin_gateways_bt = KeyboardButton(text=ButtonText.admin_gateways)
