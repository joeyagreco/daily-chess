# Daily Chess

## Quickstart

1. Clone the project
    ```bash
    git clone https://github.com/joeyagreco/daily-chess.git
    ```
2. Create a .env file with the following variables
    ```bash
    LICHESS_USERNAME
    NUM_GAMES
    RATED
    PERF_TYPE
    DISCORD_WEBHOOK_URL
    DISCORD_DAILY_OPENINGS_TO_SEND
    ```
    - LICHESS_USERNAME [string]: The username associated with your Lichess account
    - NUM_GAMES [integer]: Your last n games to include in the analysis
    - RATED [boolean]: Whether to include only rated games
    - PERF_TYPE [PerfType]: The type of games to include. [OPTIONS](https://github.com/joeyagreco/daily-chess/blob/main/enumeration/PerfType.py)
    - DISCORD_WEB_URL [string]: The URL of the Discord webhook to call. [GUIDE](https://hookdeck.com/webhooks/platforms/how-to-get-started-with-discord-webhooks#where-can-i-find-discord-webhooks)
    - DISCORD_DAILY_OPENINGS_TO_SEND [integer] The number of openings to send each day. (e.g. 3 would mean the worst 3 openings are sent each day)
3. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

    ```bash
    pip install -r requirements.txt
    ```
4. Run the script
    ```bash
    python app.py
    ``````


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

