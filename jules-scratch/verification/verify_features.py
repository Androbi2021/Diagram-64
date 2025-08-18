from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.goto("http://localhost:5173/")

    page.get_by_label("Enter FEN and description (one per line):").click()
    page.get_by_label("Enter FEN and description (one per line):").fill("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1 Black to move")
    page.get_by_label("Show turn indicator for Black").check()

    # Click the generate PDF button
    page.get_by_role("button", name="Generate PDF").click()

    # Wait for download to start
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Generate PDF").click()

    download = download_info.value

    # Wait for the download to complete
    print(f"Downloading to {download.path()}")
    download.save_as("jules-scratch/verification/chess_diagrams.pdf")

    page.screenshot(path="jules-scratch/verification/verification.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
