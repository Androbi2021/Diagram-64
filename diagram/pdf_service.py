import logging
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
    show_turn_indicator=False,
    show_page_numbers=False
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
    h_title = 0

    if title:
        centered_h1 = ParagraphStyle(
            name='CenteredH1',
            parent=styles['h1'],
            alignment=1  # 1 = TA_CENTER
        )
        t = Paragraph(title, centered_h1)
        _w, h_title = t.wrap(page_width, page_height)
        story.append(t)
        # Ajoute un espace après le titre pour une meilleure aération
        story.append(Spacer(1, h_title * 0.5))
        h_title *= 1.5 # On inclut l'espace dans la hauteur totale du titre

    # Use provided layout or fallback to config
    layout_thresholds = columns_for_diagrams_per_page or DIAGRAM_CONFIG['grid_layout_thresholds']

    # Define grid layout based on diagrams_per_page
    if diagrams_per_page <= layout_thresholds.get('single_column', 1):
        cols = 1
    elif diagrams_per_page <= layout_thresholds.get('two_column_max', 8):
        cols = 2
    else:
        cols = 3

    # Group FEN objects into pages
    fen_groups = [fens[i:i + diagrams_per_page] for i in range(0, len(fens), diagrams_per_page)]

    # Use provided padding or fallback to config
    table_padding = padding or TABLE_CONFIG['padding']
    top_padding = table_padding.get('top', 5)
    bottom_padding = table_padding.get('bottom', 5)

    is_first_page = True

    for group in fen_groups:
        col_width = page_width / cols
        max_desc_height = 0
        
        # Determine the maximum description height for the current group
        for fen_obj in group:
            description = fen_obj.get('description')
            if description:
                centered_normal = ParagraphStyle(
                    name='CenteredNormal',
                    parent=styles['Normal'],
                    alignment=1  # 1 = TA_CENTER
                )
                p = Paragraph(description, centered_normal)
                # Use wrap(), not wrapOn(), for measurement as the canvas is not available yet.
                _w, h = p.wrap(col_width, page_height)
                max_desc_height = max(max_desc_height, h)
        
        available_page_height = page_height
        if is_first_page and title:
            available_page_height -= h_title
            is_first_page = False

        number_of_rows = (diagrams_per_page + cols - 1) // cols  # A formula to avoid calling math.ceil
        available_height_for_content_per_row = available_page_height / number_of_rows
        diagram_height_max = available_height_for_content_per_row - max_desc_height - PDF_CONFIG.get('padding_before_desc') - top_padding - bottom_padding -6

        diagram_size = min(DIAGRAM_CONFIG['default_size'], page_width / cols - 20, diagram_height_max)  # Ensure diagrams fit within page width

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
                item_story.append(Spacer(1, PDF_CONFIG.get('padding_before_desc')))
                item_story.append(Paragraph(description, centered_normal))

            row_data.append(item_story)

            if len(row_data) == cols or i == len(group) - 1:
                table_data.append(row_data)
                row_data = []

        if table_data:
            content_height = diagram_size + max_desc_height + PDF_CONFIG.get('padding_before_desc')
            row_height = content_height + top_padding + bottom_padding
            
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

    def draw_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        page_number_text = f"Page {doc.page}"
        canvas.drawCentredString(
            A4[0] / 2,
            20,
            page_number_text
        )
        canvas.restoreState()

    if show_page_numbers:
        doc.build(story, onFirstPage=draw_page_number, onLaterPages=draw_page_number)
    else:
        doc.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
