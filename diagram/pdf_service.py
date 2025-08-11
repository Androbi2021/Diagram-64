from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from .config import PDF_CONFIG, DIAGRAM_CONFIG, TABLE_CONFIG
from .utils import fen_to_drawing
from .config import *

def create_pdf_from_fens(fen_strings, diagrams_per_page=PDF_CONFIG['default_diagrams_per_page']):
    """
    Creates a PDF document with a grid layout of chess diagrams from a list of FEN strings.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=PDF_CONFIG['page_size'])
    #doc.leftMargin = PDF_CONFIG['page_margin']
    #doc.rightMargin = PDF_CONFIG['page_margin']
    #doc.topMargin = PDF_CONFIG['page_margin']
    #doc.bottomMargin = PDF_CONFIG['page_margin']
    page_width = doc.width
    page_height = doc.height

    story = []

    # Define grid layout based on diagrams_per_page
    if diagrams_per_page == DIAGRAM_CONFIG['grid_layout_thresholds']['single_column']:
        cols = 1
    elif diagrams_per_page <= DIAGRAM_CONFIG['grid_layout_thresholds']['two_column_max']:
        cols = 2
    else:
        cols = 3

    diagram_size = DIAGRAM_CONFIG['default_size']
    diagram_size = min(diagram_size, page_width / cols - 10, page_height/((diagrams_per_page + cols) // cols))  # Ensure diagrams fit within page width

    # Group FEN strings into pages
    fen_groups = [fen_strings[i:i + diagrams_per_page] for i in range(0, len(fen_strings), diagrams_per_page)]

    for group in fen_groups:
        table_data = []
        row_data = []
        for i, fen in enumerate(group):
            drawing = fen_to_drawing(fen)
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
                ('LEFTPADDING', (0, 0), (-1, -1), TABLE_CONFIG['padding']['left']),
                ('RIGHTPADDING', (0, 0), (-1, -1), TABLE_CONFIG['padding']['right']),
                ('TOPPADDING', (0, 0), (-1, -1), TABLE_CONFIG['padding']['top']),
                ('BOTTOMPADDING', (0, 0), (-1, -1), TABLE_CONFIG['padding']['bottom']),
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
