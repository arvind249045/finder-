# BetterHarvester

A minimal web application wrapper for theHarvester, streaming live output and extracting emails from a given domain.

## Features
- Enter a domain, run theHarvester, and stream raw output live to the browser.
- Extracts and displays found emails at the end.
- All in one Docker container.

## Quick Start

### 1. Local Development (without Docker)
1. Install Python 3.11+
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Ensure `theHarvester` is installed and in your PATH.
4. Run the app:
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Visit [http://localhost:8000](http://localhost:8000)

### 2. Docker
1. Build the image:
   ```sh
   docker build -t betterharvester .
   ```
2. Run the container:
   ```sh
   docker run -p 8000:8000 betterharvester
   ```
3. Visit [http://localhost:8000](http://localhost:8000)

---

## Notes
- By default, only emails are parsed and shown in structured results. All other output is streamed raw.
- No authentication, database, or history.
- For production, consider HTTPS and rate limiting.
