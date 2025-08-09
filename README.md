# Chess Diagram PDF Generator

This is a full-stack web application that allows users to convert chess diagrams from Forsyth-Edwards Notation (FEN) into a downloadable PDF file. Users can input multiple FEN strings and customize the number of diagrams that appear on each page of the PDF.

## Features

- **FEN to PDF Conversion:** Converts standard FEN strings into visual chess diagrams.
- **Custom Layout:** Allows users to choose the number of diagrams per page (1, 2, 4, or 6).
- **Grid Arrangement:** Automatically arranges diagrams in a clean grid layout within the PDF.
- **REST API:** A Django-based backend provides a simple API for the conversion.
- **Modern Frontend:** A responsive and easy-to-use interface built with React and Vite.

## Technology Stack

- **Backend:**
  - Python 3
  - Django & Django Rest Framework
  - `python-chess` for FEN parsing and SVG generation.
  - `reportlab` and `svglib` for PDF generation.
- **Frontend:**
  - Node.js
  - React
  - Vite for frontend tooling.
- **Database:**
  - SQLite (for development)

## Setup and Installation

Follow these instructions to set up the project for development.

### Prerequisites

- Python 3.8+ and `pip`
- Node.js and `npm`

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Navigate to the backend project directory:**
    ```bash
    cd chess_pdf_generator
    ```

3.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The backend API will be running at `http://localhost:8000`.

### Frontend Setup

1.  **In a new terminal**, navigate to the frontend project directory:
    ```bash
    cd chess_pdf_generator/frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Start the Vite development server:**
    ```bash
    npm run dev
    ```
    The React application will be running at `http://localhost:5173` (or another port if 5173 is busy). The app is configured to proxy API requests to the Django backend.

## Usage

1.  Open your browser and navigate to the frontend URL (e.g., `http://localhost:5173`).
2.  In the text area, enter one or more FEN strings, with each FEN on a new line.
3.  Select the desired number of diagrams per page from the dropdown menu.
4.  Click the "Generate PDF" button.
5.  A PDF file named `chess_diagrams.pdf` will be generated and downloaded by your browser.
