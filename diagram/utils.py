import chess
import chess.svg
from svglib.svglib import svg2rlg
from io import StringIO

from .config import CHESS_BOARD_CONFIG

def fen_to_drawing(fen_string, board_colors=None, border_color=None):
    """
    Converts a FEN string to a ReportLab Drawing object.
    """
    # Create a chess board from the FEN string
    board = chess.Board(fen_string)


    # Use provided colors or fallback to config
    colors = board_colors or CHESS_BOARD_CONFIG['colors']

    # Generate an SVG string of the board
    svg_board = chess.svg.board(
        board=board,
        size=CHESS_BOARD_CONFIG['size'],
        coordinates=CHESS_BOARD_CONFIG['coordinates'],
        colors={
            "square light": colors["light_squares"],
            "square dark": colors["dark_squares"],
            "margin": "#000000",  # Default margin color, will be overridden
            "coord": "#000000"     # Default coordinate color
        }
    )

    # If a border_color is provided, modify the SVG string directly.
    if border_color:
        # The border is the first <rect> element with a 'stroke' attribute.
        # We replace the stroke color of the first rect that has fill="none".
        import re
        svg_board = re.sub(r'(<rect[^>]*fill="none"[^>]*stroke=")[^"]*(")',
                           r'\g<1>' + border_color + r'\2',
                           svg_board,
                           count=1)


    # Use a StringIO object to simulate a file for svglib
    svg_file = StringIO(svg_board)

    # Convert the SVG file to a ReportLab Drawing object
    drawing = svg2rlg(svg_file)

    return drawing
