from __future__ import annotations

import math
import os
from dataclasses import dataclass

import pygame

from enumeration.ChessColor import ChessColor
from enumeration.Color import Color

# image constants
TILE_SIZE = 60
ARROW_OPACITY = 60
ARROW_LINE_THICKNESS = 10
ARROWHEAD_LENGTH = 28


@dataclass(kw_only=True)
class ChessBoardArrow:
    start_coordinate: str  # "a1", "h8", etc
    end_coordinate: str  # "a1", "h8", etc
    color: Color


@dataclass(kw_only=True)
class ChessBoardImage:
    fen: str
    perspective: ChessColor  # which color will be at the bottom of the board
    arrows: list[ChessBoardArrow]

    def save_image(self, output_file: str):
        pygame.init()

        def load_piece_images():
            pieces = ["rook", "knight", "bishop", "queen", "king", "pawn"]
            colors = ["black", "white"]
            images = {}
            for piece in pieces:
                for color in colors:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    image_path = os.path.join(base_dir, "../img/pieces", f"{piece}_{color}.png")
                    image = pygame.image.load(image_path)
                    images[f"{piece}_{color}"] = pygame.transform.scale(
                        image, (TILE_SIZE, TILE_SIZE)
                    )
            return images

        def parse_fen(fen_string):
            board = []
            rows = fen_string.split(" ")[0].split("/")
            for row in rows:
                board_row = []
                for char in row:
                    if char.isdigit():
                        board_row.extend([" "] * int(char))
                    else:
                        board_row.append(char)
                board.append(board_row)
            return board

        piece_images = load_piece_images()
        board = parse_fen(self.fen)

        # Adjusting for perspective
        if self.perspective == ChessColor.BLACK:
            board = [row[::-1] for row in board[::-1]]

        board_size = 8
        colors = [pygame.Color("white"), pygame.Color("gray")]
        surface = pygame.Surface((board_size * TILE_SIZE, board_size * TILE_SIZE))

        piece_map = {
            "r": "rook_black",
            "n": "knight_black",
            "b": "bishop_black",
            "q": "queen_black",
            "k": "king_black",
            "p": "pawn_black",
            "R": "rook_white",
            "N": "knight_white",
            "B": "bishop_white",
            "Q": "queen_white",
            "K": "king_white",
            "P": "pawn_white",
        }

        for row in range(board_size):
            for col in range(board_size):
                color = colors[(row + col) % 2]
                pygame.draw.rect(
                    surface, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )

                piece = board[row][col]
                if piece in piece_map:
                    piece_image = piece_images[piece_map[piece]]
                    surface.blit(piece_image, (col * TILE_SIZE, row * TILE_SIZE))

        # Font for labels
        font = pygame.font.Font(None, 16)

        # Drawing labels
        letters = "ABCDEFGH"
        numbers = "87654321"

        # Adjust for perspective
        if self.perspective == ChessColor.BLACK:
            letters = letters[::-1]
            numbers = numbers[::-1]

        label_offset = 2  # Small offset for better positioning

        for i in range(board_size):
            # Draw letters
            letter_surface = font.render(letters[i], True, pygame.Color("black"))
            letter_x = i * TILE_SIZE + label_offset
            letter_y = (
                (board_size - 1) * TILE_SIZE
                + TILE_SIZE
                - letter_surface.get_height()
                - label_offset
            )
            surface.blit(letter_surface, (letter_x, letter_y))

            # Draw numbers
            number_surface = font.render(numbers[i], True, pygame.Color("black"))
            number_x = (
                (board_size - 1) * TILE_SIZE + TILE_SIZE - number_surface.get_width() - label_offset
            )
            number_y = i * TILE_SIZE + label_offset
            surface.blit(number_surface, (number_x, number_y))

        # draw arrows
        for arrow in self.arrows:
            self.draw_arrow(arrow=arrow, surface=surface)

        pygame.image.save(surface, output_file)
        pygame.quit()

    def draw_arrow(self, *, arrow: ChessBoardArrow, surface: pygame.Surface):
        # Convert opacity from percentage to 0-255 range
        alpha = int(ARROW_OPACITY * 255 / 100)

        # Adjust color with opacity
        color = pygame.Color(arrow.color.value)
        color.a = alpha

        # Create a separate surface for the arrow with per-pixel alpha
        arrow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        # Arrowhead properties
        arrowhead_angle = math.pi / 5

        # Calculations for start and end points
        start_x = (ord(arrow.start_coordinate[0]) - ord("a")) * TILE_SIZE + TILE_SIZE // 2
        start_y = (8 - int(arrow.start_coordinate[1])) * TILE_SIZE + TILE_SIZE // 2
        end_x = (ord(arrow.end_coordinate[0]) - ord("a")) * TILE_SIZE + TILE_SIZE // 2
        end_y = (8 - int(arrow.end_coordinate[1])) * TILE_SIZE + TILE_SIZE // 2

        # Adjust for black perspective
        if self.perspective == ChessColor.BLACK:
            start_x = surface.get_width() - start_x
            start_y = surface.get_height() - start_y
            end_x = surface.get_width() - end_x
            end_y = surface.get_height() - end_y

        # Calculate the angle and adjust end point for arrowhead
        dx = end_x - start_x
        dy = end_y - start_y
        angle = math.atan2(dy, dx)

        # Adjust the end point of the line so it doesn't extend into the arrowhead
        line_end_x = end_x - ARROWHEAD_LENGTH * math.cos(angle)
        line_end_y = end_y - ARROWHEAD_LENGTH * math.sin(angle)

        # Draw the line on the arrow surface
        pygame.draw.line(
            arrow_surface, color, (start_x, start_y), (line_end_x, line_end_y), ARROW_LINE_THICKNESS
        )

        # Calculate arrowhead points at the end
        right_end = (
            end_x - ARROWHEAD_LENGTH * math.cos(angle - arrowhead_angle),
            end_y - ARROWHEAD_LENGTH * math.sin(angle - arrowhead_angle),
        )
        left_end = (
            end_x - ARROWHEAD_LENGTH * math.cos(angle + arrowhead_angle),
            end_y - ARROWHEAD_LENGTH * math.sin(angle + arrowhead_angle),
        )

        # Draw the arrowhead on the arrow surface
        pygame.draw.polygon(arrow_surface, color, [(end_x, end_y), right_end, left_end])

        # Blit the arrow surface onto the main surface
        surface.blit(arrow_surface, (0, 0))
