import logging
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from .config import PDF_CONFIG, DIAGRAM_CONFIG, TABLE_CONFIG, CHESS_BOARD_CONFIG
from .utils import fen_to_drawing

logger = logging.getLogger(__name__)

def create_pdf_from_fens(
    fen_strings,
    diagrams_per_page=PDF_CONFIG['default_diagrams_per_page'],
    padding=None,
    board_colors=None,
    columns_for_diagrams_per_page=None,
):
    """
    Creates a PDF document with a grid layout of chess diagrams from a list of FEN strings.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=PDF_CONFIG['page_size'],
    )
    page_width = doc.width
    page_height = doc.height

    story = []

    # Use provided layout or fallback to config
    layout_thresholds = columns_for_diagrams_per_page or DIAGRAM_CONFIG['grid_layout_thresholds']

    # Define grid layout based on diagrams_per_page
    if diagrams_per_page <= layout_thresholds.get('single_column', 1):
        cols = 1
    elif diagrams_per_page <= layout_thresholds.get('two_column_max', 8):
        cols = 2
    else:
        cols = 3

    diagram_size = DIAGRAM_CONFIG['default_size']
    diagram_size = min(diagram_size, page_width / cols - 10, page_height/((diagrams_per_page + cols) // cols))  # Ensure diagrams fit within page width

    # Group FEN strings into pages
    fen_groups = [fen_strings[i:i + diagrams_per_page] for i in range(0, len(fen_strings), diagrams_per_page)]

    # Use provided padding or fallback to config
    table_padding = padding or TABLE_CONFIG['padding']

    for group in fen_groups:
        table_data = []
        row_data = []
        for i, fen in enumerate(group):
            drawing = fen_to_drawing(fen, board_colors)
            if drawing:
                # Scale drawing
                scale = diagram_size / drawing.width
                drawing.scale(scale, scale)
                drawing.width = diagram_size
                drawing.height = diagram_size
                row_data.append(drawing)

            if len(row_data) == cols or i == len(group) - 1:
                table_data.append(row_data)
                row_data = []

        if table_data:
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), TABLE_CONFIG['alignment']['vertical']),
                ('ALIGN', (0, 0), (-1, -1), TABLE_CONFIG['alignment']['horizontal']),
                ('LEFTPADDING', (0, 0), (-1, -1), table_padding.get('left', 0)),
                ('RIGHTPADDING', (0, 0), (-1, -1), table_padding.get('right', 0)),
                ('TOPPADDING', (0, 0), (-1, -1), table_padding.get('top', 5)),
                ('BOTTOMPADDING', (0, 0), (-1, -1), table_padding.get('bottom', 5)),
            ]))
            story.append(table)
            story.append(PageBreak())

    if story:
        # Remove the last PageBreak
        story.pop()

    doc.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
