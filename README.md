# Bubby bot

Telegram bot that keep track of headache. It asks you several times a day to rate your headache from 0 to 10 and sends these stats to statsd.

# Installation

```bash
virtualenv .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt
```

# Prerequisites
* python2.7 + virtualenv + pip
* statsd running on localhost

# Usage
```bash
python bot.py <telegram token>
```

# commands

* /start - subscribe to bot
* /stop - unsubsribe from bot
* 0-10 - send headache level to the bot

# TODO
* /stats - returns a weekly/monthly graph of headaches level
