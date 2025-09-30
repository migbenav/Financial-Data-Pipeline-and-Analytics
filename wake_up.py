# wake_up.py

"""
File: wake_up.py
Main Function: run_wakeup_script()

This script uses a headless Chrome browser (via Selenium) to visit a web application's URL.
This process is designed to prevent services like Streamlit Community Cloud from
putting the application to sleep (hibernation) due to inactivity, as a simple
HTTP GET request is often insufficient to trigger the "wake up" mechanism.

Functions:
- run_wakeup_script(): Main function that initializes the browser, visits the 
                       specified URL (from environment variables), waits for 
                       loading, and safely closes the browser.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Global Configuration ---
# Get the application URL from environment variables set in the GitHub Action.
APP_URL = os.environ.get("STREAMLIT_URL")

# Define necessary Chrome options for headless execution in a CI/CD environment.
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1920x1080")


# Purpose: Main function to execute the web page visit.
# Inputs: None (reads URL from environment variable STREAMLIT_URL).
# Outputs: None (prints status and ensures the browser is closed).
def run_wakeup_script():
    """Initializes a headless Chrome browser to visit the app URL and keeps it alive."""
    
    if not APP_URL:
        print("Error: STREAMLIT_URL environment variable is not set.")
        return

    print(f"Starting headless browser to wake up app at: {APP_URL}")
    driver = None
    
    try:
        # Resolve the WebDriver initialization error (Selenium 4 required change):
        # 1. Initialize the Service object using the automatically installed driver path.
        service = Service(ChromeDriverManager().install())
        
        # 2. Initialize the Chrome driver, passing the Service object and the Options.
        driver = webdriver.Chrome(
            service=service, 
            options=chrome_options
        )
        
        # Open the Streamlit URL
        driver.get(APP_URL)
        print("Page requested. Waiting for 30 seconds for the app to fully load...")
        
        # Wait time is crucial for Streamlit to fully initialize and overcome the 'sleep' state.
        time.sleep(30)
        
        # Simple verification of the final URL
        current_url = driver.current_url
        print(f"Final URL reached: {current_url}")
        
        # Check if the URL indicates a potential error (e.g., a specific error page)
        if "error" in current_url.lower():
            print("Warning: The final URL suggests a potential error. Check Streamlit logs.")
            
        print("Application successfully pinged (browser session completed).")

    except Exception as e:
        # Print the error but do not necessarily force a GitHub Action failure 
        # unless it's a critical setup issue.
        print(f"An error occurred during the wake-up process: {e}")
        
    finally:
        # Ensures the browser process is terminated safely, even if errors occur.
        if driver:
            print("Closing browser driver.")
            driver.quit()

if __name__ == "__main__":
    run_wakeup_script()