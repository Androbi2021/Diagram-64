from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# PDF Configuration
# Defines parameters related to the overall PDF document.
PDF_CONFIG = {
    'page_size': A4,  # The page size for the PDF (e.g., A4, LETTER).
    'default_diagrams_per_page': 6,  # Default number of chess diagrams to display per page.
    'page_margin': 10  # Margin around the PDF page in points.
}

# Diagram Configuration
# Defines parameters related to the chess diagrams themselves.
DIAGRAM_CONFIG = {
    'default_size': 300,  # Default size of each chess diagram in points.
    'grid_layout_thresholds': {
        'single_column': 1,  # If diagrams_per_page is 1, use a single column layout.
        'two_column_max': 8   # If diagrams_per_page is up to 8, use a two-column layout.
    }
}

# Table Styling Configuration
# Defines styling parameters for the table layout of diagrams within the PDF.
TABLE_CONFIG = {
    'padding': {
        'left': 0,    # Left padding for table cells.
        'right': 0,   # Right padding for table cells.
        'top': 5,     # Top padding for table cells.
        'bottom': 5   # Bottom padding for table cells.
    },
    'alignment': {
        'vertical': 'MIDDLE',   # Vertical alignment of content within table cells.
        'horizontal': 'CENTER'  # Horizontal alignment of content within table cells.
    }
}

# Chess Board Visual Configuration
# Defines visual parameters for the chess board rendering using python-chess.
CHESS_BOARD_CONFIG = {
    'size': 390,  # Size of the chess board SVG in pixels.
    'coordinates': True,  # Whether to display coordinates on the board.
    'colors': {
        'light_squares': '#f0d9b5',  # Color for light squares on the board.
        'dark_squares': '#b58863'   # Color for dark squares on the board.
    }
}