import chess
import chess.svg
from svglib.svglib import svg2rlg
from io import StringIO

def fen_to_drawing(fen_string):
    """
    Converts a FEN string to a ReportLab Drawing object.
    """
    # Create a chess board from the FEN string
    board = chess.Board(fen_string)

    # Generate an SVG string of the board
    svg_board = chess.svg.board(board=board)

    # Use a StringIO object to simulate a file for svglib
    svg_file = StringIO(svg_board)

    # Convert the SVG file to a ReportLab Drawing object
    drawing = svg2rlg(svg_file)

    return drawing
