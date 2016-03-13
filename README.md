# Bubby bot

Telegram bot that keep track of headaches. It asks you several times a day to rate your headache from 0 to 10 and sends these stats to statsd.

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
* /statsN- returns a png with stats for the last N days
* 0-10 - send headache level to the bot
