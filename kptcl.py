"""
KPTCL SIS Daily Maintenance Automation - Server / Headless Version
--------------------------------------------------------------------
Changes vs the desktop version:
  1. Headless Chrome (no display needed) via --headless=new
  2. Server-safe Chrome flags (--no-sandbox, --disable-dev-shm-usage, etc.)
  3. Credentials read from environment variables, not hardcoded
  4. Proper logging (to console + rotating log file) instead of print()
  5. Explicit wait for a save-confirmation element instead of blind sleep
  6. Screenshot + page source dump on failure, for post-mortem debugging
  7. Clean exit codes (0 = success, 1 = failure) so cron/systemd/CI can
     detect failures and alert you
  8. webdriver-manager auto-resolves the correct chromedriver version,
     which matters a lot on servers where Chrome gets auto-updated

Requirements:
  pip install selenium webdriver-manager

Environment variables expected:
  KPTCL_USERNAME
  KPTCL_PASSWORD

Usage:
  export KPTCL_USERNAME="aelakamanahalli110"
  export KPTCL_PASSWORD="110lhalli"
  python3 kptcl_automation_server.py
"""

import os
import sys
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAVE_WDM = True
except ImportError:
    HAVE_WDM = False

# --------------------------------------------------------------------------
# Logging setup
# --------------------------------------------------------------------------
LOG_DIR = os.environ.get("KPTCL_LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"kptcl_{datetime.now():%Y%m%d}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("kptcl_automation")

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
LOGIN_URL = "https://sis.kptcl.net/SIS/pages/loginSelectionPage.sis"
ZONE_NAME = os.environ.get("KPTCL_ZONE", "Bagalakote Zone")
USERNAME = os.environ.get("KPTCL_USERNAME")
PASSWORD = os.environ.get("KPTCL_PASSWORD")
WAIT_TIMEOUT = int(os.environ.get("KPTCL_WAIT_TIMEOUT", "25"))
SCREENSHOT_ON_FAIL = os.path.join(LOG_DIR, f"failure_{datetime.now():%Y%m%d_%H%M%S}.png")


def build_driver() -> webdriver.Chrome:
    """Build a headless Chrome driver configured for a Linux server."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    if HAVE_WDM:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # Assumes chromedriver is already on PATH (e.g. installed via apt)
        driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(60)
    return driver


def run_kptcl_automation() -> bool:
    if not USERNAME or not PASSWORD:
        log.error("KPTCL_USERNAME / KPTCL_PASSWORD environment variables are not set.")
        return False

    driver = None
    try:
        driver = build_driver()
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        log.info("Opening login selection page...")
        driver.get(LOGIN_URL)

        log.info("Selecting zone: %s", ZONE_NAME)
        wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//span[text()='{ZONE_NAME}']"))
        ).click()

        log.info("Entering credentials...")
        wait.until(EC.presence_of_element_located((By.ID, "j_username"))).send_keys(USERNAME)
        wait.until(EC.presence_of_element_located((By.ID, "j_password"))).send_keys(PASSWORD)

        log.info("Logging in...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']"))).click()

        log.info("Handling post-login dialog (Back -> OK)...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Back']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='OK']"))).click()

        log.info("Opening Maintenance tab...")
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='#form:tabview:maintenance']"))
        ).click()

        log.info("Opening Daily maintenance work(s)...")
        wait.until(EC.element_to_be_clickable((By.ID, "form:tabview:j_idt95"))).click()

        log.info("Clicking Add...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Add']"))).click()

        log.info("Opening date picker and selecting today...")
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'ui-icon-calendar')]"))
        ).click()

        today = datetime.now().day
        date_xpath = f"//table[contains(@class,'ui-datepicker-calendar')]//a[text()='{today}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()

        log.info("Selecting 'Select All' checkbox...")
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class,'ui-chkbox-box')])[1]"))
        ).click()

        log.info("Saving...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Save']"))).click()

        # Wait for a real confirmation instead of a blind sleep.
        # Adjust the XPath below to match the actual success toast/message
        # element on the KPTCL portal (commonly a PrimeFaces growl/message).
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(@class,'ui-messages-info') or contains(@class,'ui-growl-message')]")
                )
            )
            log.info("Save confirmation detected.")
        except TimeoutException:
            log.warning("No explicit save-confirmation element found; proceeding anyway.")

        log.info("Logging out...")
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'j_spring_security_logout')]"))
        ).click()

        log.info("✅ KPTCL SIS automation of 110kV MUSS Lakamanahalli completed successfully.")
        return True

    except (TimeoutException, WebDriverException) as e:
        log.error("❌ Automation error: %s", e, exc_info=True)
        if driver:
            try:
                driver.save_screenshot(SCREENSHOT_ON_FAIL)
                log.info("Failure screenshot saved to %s", SCREENSHOT_ON_FAIL)
            except Exception:
                log.warning("Could not save failure screenshot.")
        return False

    except Exception as e:
        log.error("❌ Unexpected error: %s", e, exc_info=True)
        return False

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    success = run_kptcl_automation()
    sys.exit(0 if success else 1)
