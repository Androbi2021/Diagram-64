import logging
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from .config import PDF_CONFIG, DIAGRAM_CONFIG, TABLE_CONFIG, CHESS_BOARD_CONFIG
from .utils import fen_to_drawing

logger = logging.getLogger(__name__)

from reportlab.platypus import Spacer

def create_pdf_from_fens(
    fens,
    diagrams_per_page=PDF_CONFIG['default_diagrams_per_page'],
    padding=None,
    board_colors=None,
    columns_for_diagrams_per_page=None,
    title=None,
    show_turn_indicator=False
):
    """
    Creates a PDF document with a grid layout of chess diagrams from a list of FEN objects.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=PDF_CONFIG['page_size'],
    )
    page_width = doc.width
    page_height = doc.height

    story = []
    styles = getSampleStyleSheet()

    if title:
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.styles import ParagraphStyle
        centered_h1 = ParagraphStyle(
            name='CenteredH1',
            parent=styles['h1'],
            alignment=1  # 1 = TA_CENTER
        )
        story.append(Paragraph(title, centered_h1))

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
    diagram_size = min(diagram_size, page_width / cols - 20, page_height/((diagrams_per_page + cols - 1) // cols))  # Ensure diagrams fit within page width

    # Group FEN objects into pages
    fen_groups = [fens[i:i + diagrams_per_page] for i in range(0, len(fens), diagrams_per_page)]

    # Use provided padding or fallback to config
    table_padding = padding or TABLE_CONFIG['padding']

    for group in fen_groups:
        col_width = page_width / cols
        max_desc_height = 0
        
        # Determine the maximum description height for the current group
        for fen_obj in group:
            description = fen_obj.get('description')
            if description:
                p = Paragraph(description, styles['Normal'])
                # Use wrap(), not wrapOn(), for measurement as the canvas is not available yet.
                w, h = p.wrap(col_width, page_height)
                max_desc_height = max(max_desc_height, h)

        table_data = []
        row_data = []
        
        for i, fen_obj in enumerate(group):
            fen = fen_obj['fen']
            description = fen_obj.get('description')

            drawing = fen_to_drawing(fen, board_colors, show_turn_indicator)

            item_story = []
            if drawing:
                scale = diagram_size / drawing.width
                drawing.scale(scale, scale)
                drawing.width = diagram_size
                drawing.height = diagram_size
                item_story.append(drawing)
            
            if description:
                item_story.append(Spacer(1, 6))
                item_story.append(Paragraph(description, styles['Normal']))

            row_data.append(item_story)

            if len(row_data) == cols or i == len(group) - 1:
                table_data.append(row_data)
                row_data = []

        if table_data:
            # Calculate row height based on diagram, spacer, and max description height
            row_height = diagram_size + (max_desc_height + 6 if max_desc_height else 0)
            
            # Ensure all rows in the table have a consistent height
            num_rows = len(table_data)
            table = Table(table_data, colWidths=[col_width]*cols, rowHeights=[row_height]*num_rows)
            
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
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
