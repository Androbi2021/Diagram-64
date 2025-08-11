import chess
import chess.svg
from svglib.svglib import svg2rlg
from io import StringIO

from .config import CHESS_BOARD_CONFIG

def fen_to_drawing(fen_string):
    """
    Converts a FEN string to a ReportLab Drawing object.
    """
    # Create a chess board from the FEN string
    board = chess.Board(fen_string)

    # Generate an SVG string of the board
    svg_board = chess.svg.board(
        board=board,
        size=CHESS_BOARD_CONFIG['size'],
        coordinates=CHESS_BOARD_CONFIG['coordinates'],
        colors=CHESS_BOARD_CONFIG['colors']
    )

    # Use a StringIO object to simulate a file for svglib
    svg_file = StringIO(svg_board)

    # Convert the SVG file to a ReportLab Drawing object
    drawing = svg2rlg(svg_file)

    return drawing
