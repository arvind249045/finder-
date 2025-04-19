import asyncio
import re
import logging
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files (for HTML/JS/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Regex for email extraction
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

async def run_the_harvester(domain: str):
    """Async generator to run theHarvester and stream output via SSE."""
    # Basic domain validation/sanitization (improve as needed)
    # This is a very basic check; consider more robust validation
    if not re.match(r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$", domain):
        yield {"event": "error", "data": "Invalid domain format provided."}
        return

    # Construct the command safely using list format for create_subprocess_exec
    # Use python3 and the full path to theHarvester.py to avoid permission issues
    command = ["python3", "/opt/theHarvester/theHarvester.py", "-d", domain, "-b", "all"]

    process = None
    N = 70 # Number of initial lines to skip
    skipped = 0
    try:
        logger.info(f"Starting theHarvester for domain: {domain} with command: {' '.join(command)}")
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout_buffer = []

        # Stream stdout line by line, skipping first N lines
        while process.stdout and not process.stdout.at_eof():
            line_bytes = await process.stdout.readline()
            if not line_bytes:
                break
            line = line_bytes.decode('utf-8', errors='replace').strip()
            if line:
                stdout_buffer.append(line)
                if skipped < N:
                    skipped += 1
                    continue  # Skip streaming this line
                yield {"event": "raw_log", "data": line}


        # Wait for the process to finish
        await process.wait()
        return_code = process.returncode
        logger.info(f"theHarvester process finished with code: {return_code}")

        # Handle stderr if any errors occurred during execution
        stderr_output = ""
        if process.stderr:
             stderr_bytes = await process.stderr.read()
             stderr_output = stderr_bytes.decode('utf-8', errors='replace').strip()
             if stderr_output:
                 logger.error(f"theHarvester stderr: {stderr_output}")
                 # Optionally send stderr to frontend
                 # yield {"event": "error", "data": f"Harvester Error: {stderr_output}"}

        if return_code != 0:
            err_msg = f"theHarvester exited with error code {return_code}."
            if stderr_output:
                err_msg += f" Stderr: {stderr_output}"
            yield {"event": "error", "data": err_msg}
            return

        # Process the collected output for emails
        full_output = "\n".join(stdout_buffer)
        emails_found = list(set(EMAIL_REGEX.findall(full_output))) # Use set to get unique emails

        import json
        EXCLUDE_EMAIL = 'cmartorella@edge-security.com'  # User-specified email to exclude
        filtered_emails = [e for e in emails_found if e.lower() != EXCLUDE_EMAIL.lower()]
        results = {
            "emails": sorted(filtered_emails),
            "hosts": [],
            "domain": domain,
            "count": len(filtered_emails)
        }

        logger.info(f"Scan complete. Found {len(filtered_emails)} unique emails (excluding {EXCLUDE_EMAIL}).")
        yield {"event": "final_data", "data": json.dumps(results)}

    except FileNotFoundError:
        logger.error("'theHarvester' command not found. Is it installed and in PATH?")
        yield {"event": "error", "data": "'theHarvester' command not found on the server."}
    except Exception as e:
        logger.exception(f"An error occurred during theHarvester execution: {e}")
        yield {"event": "error", "data": f"An unexpected server error occurred: {str(e)}"}
    finally:
        if process and process.returncode is None:
            try:
                logger.warning("Terminating potentially hung theHarvester process.")
                process.terminate()
                await process.wait()
            except ProcessLookupError:
                pass # Process already finished
            except Exception as term_err:
                 logger.error(f"Error terminating process: {term_err}")

@app.get("/run_harvester")
async def stream_harvester_output(request: Request, domain: str = Query(...)):
    """Endpoint to run theHarvester and stream results via SSE."""
    event_generator = run_the_harvester(domain)
    return EventSourceResponse(event_generator)

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serves the main HTML page."""
    # Read the HTML file and return it
    # In a real app, consider using templating engines like Jinja2
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return PlainTextResponse("index.html not found", status_code=404)

if __name__ == "__main__":
    import uvicorn
    # Run with auto-reload for development
    # Note: Use '0.0.0.0' to be accessible within Docker
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
