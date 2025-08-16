import logging
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .pdf_service import create_pdf_from_fens

logger = logging.getLogger(__name__)

class GeneratePdfApiView(APIView):
    """
    API View to generate a PDF from FEN strings.
    """
    def post(self, request, *args, **kwargs):
        
        fen_strings = request.data.get('fens')
        diagrams_per_page = request.data.get('diagrams_per_page', 1)
        padding = request.data.get('padding')
        board_colors = request.data.get('board_colors')
        columns_for_diagrams_per_page = request.data.get('columns_for_diagrams_per_page')
        title = request.data.get('title')
        

        if not fen_strings or not isinstance(fen_strings, list):
            return Response(
                {"error": "FEN strings must be provided in a list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Ensure diagrams_per_page is an integer
            diagrams_per_page = int(diagrams_per_page)
        except (ValueError, TypeError):
            return Response(
                {"error": "diagrams_per_page must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pdf_data = create_pdf_from_fens(
                fen_strings,
                diagrams_per_page,
                padding,
                board_colors,
                columns_for_diagrams_per_page,
                title if title != '' else None
            )

            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="chess_diagrams.pdf"'

            return response
        except Exception as e:
            # Log the exception e
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred while generating the PDF."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ReactAppView(TemplateView):
    template_name = 'index.html'
