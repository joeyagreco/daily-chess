<div align="center">
    <img src="https://github.com/joeyagreco/daily-chess/blob/main/img/daily_chess_logo.png" alt="daily chess logo" width="300"/>

Daily Chess Reviews.

<a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.10-teal.svg"></a>
![Last Commit](https://img.shields.io/github/last-commit/joeyagreco/daily-chess)
<br>
</div>

## Quickstart

1. Clone the project
    ```bash
    git clone https://github.com/joeyagreco/daily-chess.git
    ```
2. Ensure your [environment variables](https://github.com/joeyagreco/daily-chess#environment-variables) are correctly set
3. Install dependencies

    ```bash
    python -m pip install -r requirements.txt
    ```
4. Run the script
    ```bash
    python app.py
    ``````

## Run with Docker

1. Ensure your [environment variables](https://github.com/joeyagreco/daily-chess#environment-variables) are correctly set
2. Build Docker
    ```bash
    ./main build-docker
    ```
3. Run Docker
    ```bash
    ./main docker
    ```

## Environment Variables

These can be set in an `.env` file in the root of the project or any other way you prefer to set environment variables

| Variable Name                  	| Required 	| Type     	| Description                                                                                              	|
|--------------------------------	|----------	|----------	|----------------------------------------------------------------------------------------------------------	|
| LICHESS_USERNAME               	| Yes     	| string   	| The username associated with your [Lichess](https://lichess.org/) account                                                        	|
| NUM_GAMES                      	| Yes     	| integer  	| Your last n games to be included in the analysis                                                         	|
| PERF_TYPE                      	| Yes     	| PerfType 	| The type of games to include. [OPTIONS](https://github.com/joeyagreco/daily-chess/blob/main/enumeration/PerfType.py)                                                                  	|
| RUN_AT_TIME                    	| Yes     	| str      	| The hour and minute to run this at daily. Uses military time (HH:MM)                                     	|
| DISCORD_WEBHOOK_URL            	| Yes     	| str      	| The URL of the Discord webhook to call. [GUIDE](https://hookdeck.com/webhooks/platforms/how-to-get-started-with-discord-webhooks#discord-webhook-example)                                                            	|
| DISCORD_DAILY_OPENINGS_TO_SEND 	| Yes     	| integer  	| The number of openings to send each day (e.g. 3 would mean 3 openings are sent each day in the analysis) 	|
| EVALUATION_DEPTH 	| Yes     	| integer  	| The depth the chess engine should go to when evaluating a game 	|
| MAX_LOSSES_TO_EVALUATE 	| Yes     	| integer  	| The maximum number of losses to evaluate 	|
| TEST                           	| No    	| boolean  	| Whether to run this in test mode or not.                                                                 	|

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

