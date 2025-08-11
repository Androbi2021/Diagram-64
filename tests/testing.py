# -----------------------------------------------------------------------------
# Chess Diagram PDF Generation Test Script
#
# Description:
#   This script is designed to test the PDF generation functionality of the
#   `create_pdf_from_fens` function in `diagram/pdf_service.py`. It runs a
#   series of integration tests to verify layout, error handling, and
#   performance.
#
# Usage:
#   1. Make sure all required packages from `requirements.txt` are installed.
#   2. Run the script from the project root directory:
#      python tests/testing.py
#   3. The script will create a `test_pdfs` directory inside `tests/` and
#      save the generated PDF files there.
#   4. Each generated PDF will be automatically opened for manual verification.
#   5. A summary report will be printed to the console after all tests are
#      completed.
#
# -----------------------------------------------------------------------------

import os
import sys
import time
import subprocess
from datetime import datetime

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from diagram.pdf_service import create_pdf_from_fens

# --- Test Data ---

# Existing FEN strings from user
existing_fens = [
    "r1b2b1r/2p4p/p2q1np1/3pk3/p2NP3/3P4/1PP2PPP/RNBQK2R w KQ - 5 14",
    "6k1/pp5r/P4R1P/8/8/8/6K1/8 w - - 0 1",
    "8/8/1P6/8/2P5/5k2/2K5/4r3 b - - 0 1"
]

# Standard chess positions for comprehensive testing
standard_positions = {
    "starting_pos": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "scholars_mate": "r1bqkbnr/pppp1Qpp/2n5/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 3",
    "ruy_lopez": "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4",
    "kings_gambit": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
    "sicilian_defense": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
    "endgame_k_vs_r": "8/8/8/8/8/4k3/8/R7 w - - 0 1"
}

# Invalid FEN strings for error handling tests
invalid_fens = [
    "not a fen",
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",  # Missing fields
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0", # Incomplete
    "1rbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # Invalid piece
]

# Combine all valid FENs for larger tests
all_valid_fens = existing_fens + list(standard_positions.values())

# --- Test Configuration ---
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_pdfs")

# --- Global Variables ---
test_results = []

# --- Helper Functions ---

def setup_test_environment():
    """Create the output directory for generated PDFs."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    log_message("Test environment set up.", header=True)
    log_message(f"PDFs will be saved in: {os.path.abspath(OUTPUT_DIR)}")

def log_message(message, header=False):
    """Prints a formatted log message."""
    if header:
        print("\n" + "="*80)
        print(f" {message.upper()} ".center(80, "="))
        print("="*80)
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

def run_test(test_name, fen_list, diagrams_per_page):
    """Generic function to run a test case and store its result."""
    log_message(f"Running test: '{test_name}' ({diagrams_per_page} per page)", header=True)
    start_time = time.time()
    result = {
        "name": f"{test_name} ({diagrams_per_page}/page)",
        "status": "Failed",
        "duration": 0,
        "file_size": 0,
        "path": "N/A",
        "error": "N/A"
    }
    
    try:
        pdf_data = create_pdf_from_fens(fen_list, diagrams_per_page=diagrams_per_page)
        duration = time.time() - start_time
        result["duration"] = duration
        
        if pdf_data:
            file_name = f"{test_name.replace(' ', '_').lower()}_{diagrams_per_page}_per_page.pdf"
            file_path = os.path.join(OUTPUT_DIR, file_name)
            
            with open(file_path, "wb") as f:
                f.write(pdf_data)
                
            file_size = os.path.getsize(file_path) / 1024
            result.update({
                "status": "Success",
                "file_size": file_size,
                "path": file_path
            })
            log_message(f"Successfully created PDF: {file_path} ({file_size:.2f} KB)")
            #open_file(file_path)
        else:
            result["error"] = "No PDF data was generated."
            log_message("Test failed: No PDF data was generated.")
            
    except Exception as e:
        duration = time.time() - start_time
        result["duration"] = duration
        result["error"] = str(e)
        log_message(f"Test failed after {duration:.4f} seconds with an exception: {e}", )
    
    test_results.append(result)


def open_file(path):
    """Opens a file in the default system viewer."""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
        log_message(f"Opened {os.path.basename(path)} for manual verification.")
    except Exception as e:
        log_message(f"Could not automatically open file: {e}")

def generate_summary_report():
    """Prints a summary of all test results."""
    log_message("Test Summary Report", header=True)
    
    success_count = sum(1 for r in test_results if r["status"] == "Success")
    total_tests = len(test_results)
    
    print(f" {total_tests} tests run, {success_count} succeeded. ".center(80, "-"))
    
    for result in test_results:
        print(f"\nTest: {result['name']}")
        print(f"  - Status:   {result['status']}")
        print(f"  - Duration: {result['duration']:.4f}s")
        if result['status'] == 'Success':
            print(f"  - File:     {os.path.basename(result['path'])}")
            print(f"  - Size:     {result['file_size']:.2f} KB")
        else:
            print(f"  - Error:    {result['error']}")

# --- Test Execution ---

def main():
    """Main function to run all tests."""
    setup_test_environment()
    
    # --- Test Cases ---
    
    # 1. Layout Tests
    run_test("Existing FENs", existing_fens, diagrams_per_page=1)
    run_test("Standard Positions", all_valid_fens, diagrams_per_page=2)
    run_test("All Valid FENs", all_valid_fens, diagrams_per_page=4)
    run_test("All Valid FENs", all_valid_fens, diagrams_per_page=6)
    run_test("All Valid FENs", all_valid_fens, diagrams_per_page=9)
    
    # 2. Error Handling Tests
    run_test("Invalid FENs", invalid_fens, diagrams_per_page=1)
    run_test("Empty Input", [], diagrams_per_page=1)
    
    # 3. Performance Tests (using all valid FENs)
    run_test("Performance", all_valid_fens, diagrams_per_page=8)

    # --- Report Generation ---
    generate_summary_report()
    
    log_message("All tests completed.", header=True)

if __name__ == "__main__":
    main()
