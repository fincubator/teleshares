# TeleShares

[![Telegram]][Telegram try]

Telegram Bot for BitShares. Asynchronous. Written on Python.

### How it works
There is out of box:
* Explorer for BitSshares blockchain (Currently Accounts, Markets and Fee schedule)

Also it has some plugin system. Currently implemented 3 plugins, which can be 
turned *on/off*
* Notifier (currently Account new operations and Market price change)
* Gateways (Browse some bitshares gateways info)
* Wallet (Currently send transfers, place and cancel limit orders)

Plugins can be switched in `config.yaml` in `plugins:` section by changing
Python `True` or `False` value of each plugin (restart required).

#### Is wallet plugin secure? Where my password/private keys stored? Are you have access to my funds?
Keys are stored in `config/wallet.yaml` file. 
Broadcasting of transactions (and all other bitshares tools) are based on [Python BitShares] package.

Wallet plugin is TURNED OFF in public instance. If you want to use it, deploy it yourself

## Install
#### On Linux with  Docker

Install git, Docker, Docker Compose:
```bash
sudo apt install git docker.io docker-compose
```

Clone the repository:
```bash
git clone https://github.com/biobdeveloper/teleshares
cd teleshares
```

Create config
```bash
cp config/config.yaml.example config.yaml
```

Go to t.me/botfather and create new bot


Fill config.yaml file with your data

Start the bot by running the command:
```bash
docker-compose up
```

## Admin Control Tools
I publish source code only for the "bot app" part. So you need some admin backend to control database.
I highly recommend to use [flask-admin](https://github.com/flask-admin/flask-admin) because it is simple, fast, and most importantly - compatible with Sqlalchemy, so you can reuse declared database models.

Also you can create some command handlers in `teleshares/src/tg/handlers/admin_handlers.py` file to manage the bot directly from Telegram.


[Telegram]: https://img.shields.io/badge/Telegram-Try%20out-blue?logo=telegram
[Telegram try]: https://t.me/telesharesbot
[Python BitShares]: https://github.com/bitshares/python-bitshares