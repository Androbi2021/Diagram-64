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
    show_page_numbers=False,
    show_coordinates=CHESS_BOARD_CONFIG['coordinates']
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
            fontName='Times-Roman',
            fontSize=20,
            parent=styles['h1'],
            alignment=1,  # 1 = TA_CENTER
            spaceBefore=0,  # rely solely on the manual Spacer below so the title's
            spaceAfter=0,   # footprint equals h_title exactly (no hidden h1 spacing)
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

    # Layout geometry shared by every page.
    col_width = page_width / cols
    width_cap = page_width / cols - 20  # Ensure diagrams fit within the column width
    number_of_rows = (diagrams_per_page + cols - 1) // cols  # ceil(diagrams_per_page / cols)
    padding_before_desc = PDF_CONFIG.get('padding_before_desc')
    # Slack reserved per page so a full grid never splits across pages: ReportLab's default
    # Frame adds 6pt padding top and bottom (12pt total, not counted in doc.height), plus a
    # few points for rounding.
    PAGE_FILL_SAFETY = 16

    centered_normal = ParagraphStyle(
        name='CenteredNormal',
        fontName='Times-Roman',
        parent=styles['Normal'],
        alignment=1  # 1 = TA_CENTER
    )

    def description_of(fen_item):
        # Support both dict objects with 'description' and raw FEN strings
        if isinstance(fen_item, dict):
            return fen_item.get('description')
        return None

    def description_height(fen_item):
        description = description_of(fen_item)
        if not description:
            return 0
        # Use wrap(), not wrapOn(), for measurement as the canvas is not available yet.
        _w, h = Paragraph(description, centered_normal).wrap(col_width, page_height)
        return h

    # Compute a single diagram size from the most constrained page, then reuse it on every
    # page so board size and the spacing between diagrams stay consistent across the whole
    # document. The first page is the tightest when a title is present, and a page whose
    # group holds the tallest caption is the tightest caption-wise; taking the minimum over
    # all pages guarantees every page fits.
    diagram_size = min(DIAGRAM_CONFIG['default_size'], width_cap)
    for page_index, group in enumerate(fen_groups):
        page_desc_height = max((description_height(item) for item in group), default=0)
        available_page_height = page_height
        if page_index == 0 and title:
            available_page_height -= h_title
        height_per_row = available_page_height / number_of_rows
        diagram_height_max = height_per_row - page_desc_height - padding_before_desc - top_padding - bottom_padding - 6
        diagram_size = min(diagram_size, diagram_height_max)

    for page_index, group in enumerate(fen_groups):
        # Spread the rows to fill the page so every diagram gets an equal writing gap
        # beneath it. Dividing by number_of_rows (the page capacity) rather than the actual
        # row count keeps the rhythm identical on a partial last page. The title reduces the
        # first page's height, so its gaps are slightly smaller than later pages'.
        available_page_height = page_height
        if page_index == 0 and title:
            available_page_height -= h_title
        # Leave a small slack so rounding never pushes the table past the frame, which would
        # split a page's grid across two pages.
        row_height = (available_page_height - PAGE_FILL_SAFETY) / number_of_rows

        table_data = []
        row_data = []

        for i, fen_item in enumerate(group):
            fen = fen_item.get('fen') if isinstance(fen_item, dict) else fen_item
            description = description_of(fen_item)

            # Prepare board_colors, merging the new border_color if provided
            current_board_colors = dict(board_colors or {})
            drawing = fen_to_drawing(fen, current_board_colors, show_turn_indicator, show_coordinates)

            item_story = []
            if drawing:
                scale = diagram_size / drawing.width
                drawing.scale(scale, scale)
                drawing.width = diagram_size
                drawing.height = diagram_size
                item_story.append(drawing)

            if description:
                item_story.append(Spacer(1, padding_before_desc))
                item_story.append(Paragraph(description, centered_normal))

            row_data.append(item_story)

            if len(row_data) == cols or i == len(group) - 1:
                table_data.append(row_data)
                row_data = []

        if table_data:
            # Uniform tall rows + TOP alignment ⇒ the slack lands as an equal writing gap
            # below each diagram (or below its caption).
            row_heights = [row_height] * len(table_data)
            table = Table(table_data, colWidths=[col_width]*cols, rowHeights=row_heights)

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
