import os
import subprocess
import time
import signal
import sys
from playwright.sync_api import sync_playwright

def run_verification():
    print("Starting Django server...")
    env = os.environ.copy()
    env["DJANGO_SECRET_KEY"] = "dummy_secret_key_for_testing_123"
    env["OPENAI_API_KEY"] = "dummy_api_key"

    # Start Django server
    process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "8001"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("Waiting for server...")
    time.sleep(5) # Wait for server to start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Verify Homepage (Chat List)
            # URL is "/" because chat.urls is included at root in core/urls.py
            print("Navigating to Homepage...")
            page.goto("http://127.0.0.1:8001/")
            page.wait_for_load_state("networkidle")

            # Check for title to ensure we are on the right page
            title = page.title()
            print(f"Page Title: {title}")

            # Take screenshot of homepage
            os.makedirs("/home/jules/verification", exist_ok=True)
            page.screenshot(path="/home/jules/verification/homepage_corrected.png")
            print("Homepage screenshot saved.")

            browser.close()

    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        print("Stopping server...")
        os.kill(process.pid, signal.SIGTERM)

if __name__ == "__main__":
    run_verification()
