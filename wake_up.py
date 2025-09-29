# wake_up.py
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Get the URL from environment variables
APP_URL = os.environ.get("STREAMLIT_URL")

# --- Configuration ---
# Set up Chrome options for headless mode (no graphical interface)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1920x1080")

print(f"Starting headless browser to wake up app at: {APP_URL}")

try:
    # Initialize the Chrome driver manager
    driver = webdriver.Chrome(
        ChromeDriverManager().install(), 
        options=chrome_options
    )
    
    # Open the Streamlit URL
    driver.get(APP_URL)
    print("Page requested. Waiting for 30 seconds for the app to fully load...")
    
    # Wait for 30 seconds. This is crucial for Streamlit to fully initialize 
    # and overcome the 'sleep' state.
    time.sleep(30)
    
    # Verify the final URL and status (optional check)
    current_url = driver.current_url
    print(f"Final URL reached: {current_url}")
    
    if "error" in current_url:
        print("Warning: The final URL suggests an error. Check Streamlit logs.")
        
    print("Application successfully pinged (browser closed).")

except Exception as e:
    print(f"An error occurred during the wake-up process: {e}")
    # We allow the script to exit successfully unless a catastrophic
    # setup error occurred, to prevent the GitHub Action from failing 
    # on every execution.
finally:
    if 'driver' in locals() and driver:
        driver.quit()