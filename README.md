# Trading bot

1. You'll need phantom wallet along with chrome extension to it. Open chrome in debugging mode:

```
/path/to/chrome --remote-debugging-port=9222 --user-data-dir=/path/to/chrome/user/data
```

2. After running the command you should have gotten the debug websocket endpoint. It is available under http://localhost:9222/json/version. Fill up ENV variables in pupeteer_trader.
3. Install node modules and run pupeteer trader server. Run commands inside `pupeteer_trader`.

```
npm install
npm run serve
```
4. Pupeteer_trader is now listening on two endpoints on buy and sell instructions. You can fire GET requests to `localhost:3000/buy/:coinhash` or `localhost:3000/sell/:coinhash`. Buys are done with preset amount of SOL (in .env variables). Sells are always done for 100% of coin.

5. The buys are automated with telethon_bot. To run telethon_bot first install requirements
```
pip install -r requirments.txt
```

6. You will need telegram API configured. You can do it here: https://my.telegram.org/auth?to=apps. After logging in fill ENV variables inside .env file in telethon_bot.

6. Run the application
```
python ./telethon_bot.py
```

Running it first time will require to log in. Follow prompts.

7. Telethon bot will listen to provided channel ids from telegram you have access to from your account. If any SOL adress will appear in them, the pupeteer trader will perform a buy transaction.
