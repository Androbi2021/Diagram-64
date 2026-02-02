import logging
import chess
import chess.svg
from svglib.svglib import svg2rlg
from io import StringIO
from reportlab.graphics.shapes import Circle, Rect
from reportlab.lib import colors

from .config import CHESS_BOARD_CONFIG

logger = logging.getLogger(__name__)

def fen_to_drawing(fen_string, board_colors=None, show_turn_indicator=False, show_coordinates=CHESS_BOARD_CONFIG['coordinates']):
    """
    Converts a FEN string to a ReportLab Drawing object.
    """
    # Create a chess board from the FEN string
    board = chess.Board(fen_string)

    # Use provided colors merged over defaults to avoid missing keys
    base_colors = CHESS_BOARD_CONFIG['colors']
    colors_config = {**base_colors, **(board_colors or {})}
    outline_color = colors_config.get('dark_squares')
    border_color = colors_config.get('border_color')
    
    # Generate an SVG string of the board
    svg_board = chess.svg.board(
        board=board,
        size=CHESS_BOARD_CONFIG['size'],
        coordinates=show_coordinates,
        colors={
            "square light": colors_config.get("light_squares"),
            "square dark": colors_config.get("dark_squares"),
            "coord": CHESS_BOARD_CONFIG['coord'],
        }
    )

    if show_coordinates and border_color:
        # The border is the first <rect> element with a 'stroke' attribute.
        # We replace the stroke color of the first rect that has fill="none".
        import re
        svg_board = re.sub(r'(<rect[^>]*fill="none"[^>]*stroke=")[^"]*(")',
                           r'\g<1>' + border_color + r'\2',
                           svg_board,
                           count=1)
    
    # If there's no coordinates, we'll draw the desired
    # border at the Drawing level to avoid brittle SVG regex manipulation.

    # Use a StringIO object to simulate a file for svglib
    svg_file = StringIO(svg_board)

    # Convert the SVG file to a ReportLab Drawing object
    drawing = svg2rlg(svg_file)

    # Add outline

    if not show_coordinates:
        # Add a rectangle slightly inset to serve as the outline
        outline = Rect(
            0.5, 0.5,  # Small inset from the top-left corner
            drawing.width - 1,  # Width, adjusted for inset
            drawing.height - 1, # Height, adjusted for inset
            fillColor=None,
            strokeColor=outline_color,
            strokeWidth=1
        )
        drawing.add(outline)

    if show_turn_indicator and board.turn == chess.BLACK:
        # Add a black circle to indicate black's turn
        circle = Circle(
            CHESS_BOARD_CONFIG['size'] + 15,
            CHESS_BOARD_CONFIG['size'] - 10,
            10,
            fillColor=colors.black,
            strokeColor=colors.white,
            strokeWidth=1
        )
        drawing.add(circle)

    return drawing
