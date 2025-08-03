# Court Data Fetcher & Mini-Dashboard

A web application to fetch and display case metadata and latest orders from the Delhi High Court website.

## Court Chosen
- **Delhi High Court**: https://delhihighcourt.nic.in/

## Setup Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/court-data-fetcher.git
   cd court-data-fetcher
   ```
2. Install dependencies:
   ```bash
   pip install flask requests beautifulsoup4 playwright
   playwright install
   ```
3. Initialize the database:
   ```bash
   python -c "from court_data_fetcher import init_db; init_db()"
   ```
4. Run the application:
   ```bash
   python court_data_fetcher.py
   ```
5. Access the app at `http://localhost:5000`.

## CAPTCHA Strategy
- The app requires manual entry of a CAPTCHA token, which users obtain from the court's website.
- This avoids automated CAPTCHA solving to comply with legal and ethical guidelines.
- Future enhancements could explore court APIs (if available) for direct access.

## Sample Environment Variables
No environment variables are required, but ensure Playwright browsers are installed.

## Demo Video
A ≤5-minute screen capture is available in the repository (`demo.mp4`) showing the end-to-end flow.

## Optional Extras
- **Dockerfile**: Included for containerized deployment.
- **Unit Tests**: Basic tests for database and API endpoints.
- **CI Workflow**: GitHub Actions workflow for automated testing.

## License
MIT License