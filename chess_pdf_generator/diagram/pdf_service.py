from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .utils import fen_to_drawing

def create_pdf_from_fens(fen_strings, diagrams_per_page=1):
    """
    Creates a PDF document with a grid layout of chess diagrams from a list of FEN strings.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    story = []

    # Define grid layout based on diagrams_per_page
    if diagrams_per_page == 1:
        cols = 1
    elif diagrams_per_page == 2:
        cols = 2
    elif diagrams_per_page <= 4:
        cols = 2
    elif diagrams_per_page <= 6:
        cols = 3
    else: # Default for more than 6, or handle as an error
        cols = 3

    diagram_size = 200 # Adjust size as needed

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
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
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
