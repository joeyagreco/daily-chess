import os
import tempfile
import time

import schedule

from enumeration.ChessColor import ChessColor
from enumeration.ChessGameOutcome import ChessGameOutcome
from enumeration.ChessStatus import ChessStatus
from enumeration.Color import Color
from enumeration.HexColor import HexColor
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.chess_image import ChessBoardArrow, ChessBoardImage
from model.ChessGameV2 import ChessGameV2
from model.ChessOpening import ChessOpening
from service.chess_game import get_games_for_user_v2
from service.evaluate_game import get_worst_move_for_user
from service.user_eval import get_current_date_as_string, get_elo_string, get_emoji_for_color, get_emoji_for_elo, get_opening_infos, get_record_string
from util.discord import send_discord_message
from util.EnvironmentReader import EnvironmentReader

TEST = EnvironmentReader.get("TEST", "false").lower() == "true"
RUN_AT_TIME = EnvironmentReader.get("RUN_AT_TIME")
USERNAME = EnvironmentReader.get("LICHESS_USERNAME")
NUM_GAMES = int(EnvironmentReader.get("NUM_GAMES"))
PERF_TYPE = PerfType.from_str(EnvironmentReader.get("PERF_TYPE"))
WEBHOOK_URL = EnvironmentReader.get("DISCORD_WEBHOOK_URL")
DISCORD_DAILY_OPENINGS_TO_SEND = int(EnvironmentReader.get("DISCORD_DAILY_OPENINGS_TO_SEND"))
EVALUATION_DEPTH = int(EnvironmentReader.get("EVALUATION_DEPTH"))
MAX_LOSSES_TO_EVALUATE = int(EnvironmentReader.get("MAX_LOSSES_TO_EVALUATE"))
STOP_AFTER_EVAL_CHANGE_OF = int(EnvironmentReader.get("STOP_AFTER_EVAL_CHANGE_OF"))
STOCKFISH_EXECUTABLE_NAME = "stockfish_macos" if TEST else "stockfish"
SPOILER_DELIMETER = "||"


def main() -> None:
    games: list[ChessGameV2] = get_games_for_user_v2(
        USERNAME,
        max=NUM_GAMES,
        rated=True,
        perf_type=PERF_TYPE,
        tags=True,
        sort=Sort.DATE_DESC,
        opening=True,
        finished=True,
        literate=True,
        last_fen=True,
    )

    print(f"SUCCESSFULLY RETRIEVED {len(games)} GAMES...")

    # calculate net elo for each opening
    # openings_and_net_elo = defaultdict(float)

    # calculate best and worst user/elo beat and lost to
    highest_elo_beat = None
    lowest_elo_lost = None
    highest_elo_beat_username = None
    lowest_elo_lost_username = None

    # keep track of each game's outcome (status)
    status_and_count = {}
    for _, status in ChessStatus.items():
        status_and_count[status] = {}
        for _, outcome in ChessGameOutcome.items():
            status_and_count[status][outcome] = 0

    # holds urls, game outcome
    openings_and_game: dict[str, list[ChessGameV2]] = {}
    for game in games:
        if game.opening.name not in openings_and_game.keys():
            openings_and_game[game.opening.name] = []

        # get game outcome (status)
        game_outcome = game.outcome_for_user(USERNAME)
        status_and_count[game.status.value][game_outcome.value] += 1

        # calculate best win / worst loss
        if game_outcome != ChessGameOutcome.TIE:
            winner_elo = game.winning_player.rating
            loser_elo = game.losing_player.rating

            if game_outcome == ChessGameOutcome.WIN and (
                highest_elo_beat is None or loser_elo > highest_elo_beat
            ):
                highest_elo_beat = loser_elo
                highest_elo_beat_username = game.losing_player.user.name
            elif game_outcome == ChessGameOutcome.LOSS and (
                lowest_elo_lost is None or winner_elo < lowest_elo_lost
            ):
                lowest_elo_lost = winner_elo
                lowest_elo_lost_username = game.winning_player.user.name

        openings_and_game[game.opening.name].append(game)
        # sort
        # primary sort on: win -> loss -> tie
        # secondary sort on: status
        openings_and_game[game.opening.name].sort(
            key=lambda game: (
                {
                    ChessGameOutcome.WIN.value: 0,
                    ChessGameOutcome.LOSS.value: 1,
                    ChessGameOutcome.TIE.value: 2,
                }[game.outcome_for_user(USERNAME).value],
                game.status.value,
            )
        )

    # store all openings and the frequency
    opening_and_frequency_embeds = []

    # store info about worst and best openings
    opening_detail_fields = []

    opening_infos = get_opening_infos(games=games, for_username=USERNAME)
    # sort from worst elo -> best elo
    opening_infos.sort(key=lambda opening: opening.net_elo)
    for opening_info in opening_infos:
        record_str = get_record_string(opening_info.player_outcomes)
        elo_string = get_elo_string(opening_info.net_elo)
        emoji = get_emoji_for_elo(opening_info.net_elo)
        times_played = len(opening_info.player_outcomes)
        value = f"\nELO: {elo_string} {emoji}\nGAMES PLAYED: {times_played}\nRECORD: {record_str}\n[Opening Explorer]({ChessOpening.get_lichess_url(opening_info.opening_name)})"
        opening_display_name = f"{opening_info.opening_name} {get_emoji_for_color(opening_info.player_color)}"
        
        opening_and_frequency_embeds.append(
            {
                "name": opening_display_name,
                "value": str(times_played),
                "inline": False,
            }
        )
        
        opening_detail_fields.append({"name": opening_display_name, "value": value, "inline": False})

    game_eval_embeds = []

    # get eval for each loss
    evaluate_games = [g for g in games if g.outcome_for_user(USERNAME) == ChessGameOutcome.LOSS][
        :MAX_LOSSES_TO_EVALUATE
    ]

    chess_board_images: list[ChessBoardImage] = []
    for i, game in enumerate(evaluate_games):
        print(f"EVALUATING GAME {i+1}/{len(evaluate_games)}")
        worst_move = get_worst_move_for_user(
            chess_game=game,
            username=USERNAME,
            evaluation_depth=EVALUATION_DEPTH,
            stockfish_executable_name=STOCKFISH_EXECUTABLE_NAME,
            stop_after_eval_change_of=STOP_AFTER_EVAL_CHANGE_OF,
        )
        user_color = game.color_for_user(USERNAME)
        game_eval_embeds.append(
            {
                "title": f"{ChessGameOutcome.LOSS.value} ({game.status.value}) as {user_color.value}",
                "description": f"[POSITION]({worst_move.url})\n\n[GAME]({game.game_url})",
                "color": HexColor.WHITE.value
                if user_color == ChessColor.WHITE
                else HexColor.BLACK.value,
                "footer": {"text": f"{i+1}/{len(evaluate_games)}"},
            }
        )
        worst_move_start_coordinate = worst_move.actual_move[:2]
        worst_move_end_coordinate = worst_move.actual_move[2:]
        best_move_start_coordinate = worst_move.engine_best_move[:2]
        best_move_end_coordinate = worst_move.engine_best_move[2:]
        arrows = [
            ChessBoardArrow(
                start_coordinate=worst_move_start_coordinate,
                end_coordinate=worst_move_end_coordinate,
                color=Color.RED,
            ),
            ChessBoardArrow(
                start_coordinate=best_move_start_coordinate,
                end_coordinate=best_move_end_coordinate,
                color=Color.GREEN,
            ),
        ]
        chess_board_images.append(
            ChessBoardImage(fen=worst_move.fen_before_move, perspective=user_color, arrows=arrows)
        )

    # sort from most -> least frequent openings
    opening_and_frequency_embeds = sorted(
        opening_and_frequency_embeds, key=lambda x: int(x["value"]), reverse=True
    )

    status_embed_fields = []
    # create embeds for each game outcome type (status)
    for status, outcomes in status_and_count.items():
        # ensure that there was at least 1 game with this status before adding it
        if (
            outcomes[ChessGameOutcome.WIN.value]
            + outcomes[ChessGameOutcome.LOSS.value]
            + outcomes[ChessGameOutcome.TIE.value]
            > 0
        ):
            status_embed_fields.append(
                {
                    "name": status.replace("_", " ").title(),
                    "value": f"{outcomes[ChessGameOutcome.WIN.value]}-{outcomes[ChessGameOutcome.LOSS.value]}-{outcomes[ChessGameOutcome.TIE.value]}",
                    "inline": False,
                }
            )

    # sort embeds from most -> least games
    status_embed_fields.sort(key=lambda x: sum(int(v) for v in x["value"].split("-")), reverse=True)

    worst_openings_embed = {
        "description": f"Worst {DISCORD_DAILY_OPENINGS_TO_SEND} openings",
        "fields": opening_detail_fields[:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.RED.value,
    }

    best_openings_embed = {
        "description": f"Best {DISCORD_DAILY_OPENINGS_TO_SEND} openings",
        "fields": opening_detail_fields[::-1][:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.GREEN.value,
    }

    most_played_openings_embed = {
        "description": f"Top {DISCORD_DAILY_OPENINGS_TO_SEND} most played openings",
        "fields": opening_and_frequency_embeds[:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.LIGHT_BLUE.value,
    }

    best_win_and_worst_loss_embed = {
        "description": f"Best Win and Worst Loss",
        "fields": [
            {
                "name": "Best Win",
                "value": f"**{highest_elo_beat_username}**: {highest_elo_beat}",
                "inline": True,
            },
            {
                "name": "Worst Loss",
                "value": f"**{lowest_elo_lost_username}**: {lowest_elo_lost}",
                "inline": True,
            },
        ],
        "color": HexColor.PURPLE.value,
    }

    terminations_embed = {
        "description": "Record By Outcome",
        "fields": status_embed_fields,
        "color": HexColor.TEAL.value,
    }

    # calculate elo change
    starting_elo = games[-1].get_chess_player(USERNAME).rating
    ending_elo = games[0].get_chess_player(USERNAME).rating_after_game
    elo_dif = str(ending_elo - starting_elo)

    # format elo dif
    if int(elo_dif) > 0:
        elo_dif = f"+{elo_dif} :chart_with_upwards_trend:"
    elif int(elo_dif) < 0:
        elo_dif = f"{elo_dif} :chart_with_downwards_trend:"
    else:
        elo_dif = f"{elo_dif} :heavy_minus_sign:"

    elo_recap_fields = [
        {"name": "Starting Elo", "value": str(starting_elo), "inline": False},
        {"name": "Ending Elo", "value": str(ending_elo), "inline": False},
        {"name": "Elo Change", "value": elo_dif, "inline": False},
    ]

    title_embed = {
        "title": f"Chess Update: {get_current_date_as_string()} :chess_pawn:",
        "description": f"Recap of your last {NUM_GAMES} games.",
        "fields": elo_recap_fields,
        "color": HexColor.BLUE.value,
    }

    print(f"SENDING EMBEDS TO DISCORD...")
    # send embeds without images to discord
    for embed in [
        title_embed,
        terminations_embed,
        best_win_and_worst_loss_embed,
        worst_openings_embed,
        best_openings_embed,
        most_played_openings_embed,
    ]:
        send_discord_message(webhook_url=WEBHOOK_URL, embeds=[embed])
        time.sleep(1)

    # send embeds with images to discord
    for chess_image, game_eval_embed in zip(chess_board_images, game_eval_embeds):
        with tempfile.TemporaryDirectory() as tmp_dir:
            image_path = os.path.join(tmp_dir, f"image_{i+1}.png")
            chess_image.save_image(image_path)
            send_discord_message(
                webhook_url=WEBHOOK_URL, embeds=[game_eval_embed], file_path=image_path
            )
            time.sleep(1)


if __name__ == "__main__":
    if TEST:
        print("RUNNING AS TEST...")
        main()
    else:
        print(f"SCHEDULED TO RUN AT {RUN_AT_TIME} DAILY...")
        schedule.every().day.at(RUN_AT_TIME).do(main)

        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                send_discord_message(
                    webhook_url=WEBHOOK_URL,
                    embeds=[{"title": "ERROR", "description": e, "color": HexColor.RED.value}],
                )
